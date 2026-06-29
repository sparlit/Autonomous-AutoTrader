import unittest
import pandas as pd
import numpy as np
import sys
import os
import ujson as json
import asyncio
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.getcwd())

from src.python.analyst.indicators import IndicatorAnalyst
from src.python.brains.strategies.swing_master import SwingMaster
from src.python.brains.specialized import PortfolioBrain
from src.python.bridge.server import BridgeServer

class TestV8Updates(unittest.TestCase):
    def setUp(self):
        self.analyst = IndicatorAnalyst()
        # Create dummy OHLC data
        dates = pd.date_range('2023-01-01', periods=100, freq='5min')
        data = {
            'o': np.random.randn(100).cumsum() + 100,
            'h': np.random.randn(100).cumsum() + 101,
            'l': np.random.randn(100).cumsum() + 99,
            'c': np.random.randn(100).cumsum() + 100,
            'v': np.random.randint(100, 1000, 100)
        }
        self.df = pd.DataFrame(data, index=dates)

    def test_realized_volatility(self):
        """Verify realized volatility calculation."""
        inds = self.analyst.calculate_all(self.df)
        self.assertIn('realized_vol', inds)
        self.assertGreater(inds['realized_vol'], 0)
        print(f"DEBUG: Realized Vol: {inds['realized_vol']}")

    def test_swing_master_dynamic_bands(self):
        """Verify SwingMaster dynamic RSI bands."""
        mock_ipc = MagicMock()
        strategy = SwingMaster("TestSwing", ipc=mock_ipc)

        history = self.df.reset_index().to_dict('records')
        data = {
            "s": "EURUSD",
            "tf": 240,
            "history": history
        }

        result = asyncio.run(strategy.process(data))
        self.assertIsNotNone(result)
        print(f"DEBUG: SwingMaster Result: {result}")

    def test_bridge_sequence_numbering(self):
        """Verify Python bridge adds sequence numbers to outgoing messages."""
        mock_cb = MagicMock()
        server = BridgeServer("127.0.0.1", 8008, mock_cb)

        mock_writer = MagicMock()
        client_id = "127.0.0.1:1234"
        server.clients[client_id] = mock_writer
        server.client_seqs[client_id] = 10

        asyncio.run(server.broadcast({"t": "TLM", "s": "EURUSD"}))

        args, kwargs = mock_writer.write.call_args
        payload = args[0].decode()
        msg = json.loads(payload)
        self.assertEqual(msg['seq'], 11)
        print(f"DEBUG: Broadcast msg with seq: {msg['seq']}")

    def test_portfolio_var_precise_exposure(self):
        """Verify PortfolioBrain VaR with precise symbol-based exposure."""
        mock_ipc = MagicMock()
        mock_ipc.get_state.side_effect = lambda key, default=None: {
            "active_trades": [{"symbol": "XAUUSD", "lots": 0.1, "entry_price": 2000.0}],
            "symbol_stats:XAUUSD": {"realized_vol": 0.01, "tick_val": 1.0, "tick_size": 0.01},
            "account_stats": {"equity": 10000}
        }.get(key, default)

        brain = PortfolioBrain("Portfolio_1", ipc=mock_ipc)

        # Patch RUST_AVAILABLE in specialized module
        import src.python.brains.specialized as specialized
        orig_rust_available = specialized.RUST_AVAILABLE
        orig_rust = getattr(specialized, 'aat_rust', None)

        specialized.RUST_AVAILABLE = True
        specialized.aat_rust = MagicMock()
        # Mocking calculate_var_parallel to return a float for the comparison
        specialized.aat_rust.calculate_var_parallel.return_value = 50.0

        try:
            asyncio.run(brain.initialize())
            brain.last_var_check = 0
            event = {"t": "HB", "s": "XAUUSD", "e": 10000, "d": 0.5}

            asyncio.run(brain.process(event))

            # check what calculate_var_parallel was called with
            # Exposure = (0.1 * 1.0 / 0.01) = 10.0
            specialized.aat_rust.calculate_var_parallel.assert_called_with([10.0], [0.01])
            print("DEBUG: Precise exposure calculation verified.")
        finally:
            specialized.RUST_AVAILABLE = orig_rust_available
            if orig_rust:
                specialized.aat_rust = orig_rust
            else:
                del specialized.aat_rust

if __name__ == '__main__':
    unittest.main()
