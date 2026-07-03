import pytest
import asyncio
import time
import pandas as pd
import json
from src.python.brains.specialized import MarketDataBrain
from src.python.brains.consensus import MetaBrain

class MockIPC:
    def __init__(self):
        self.state = {}
    def get_state(self, key, default=None):
        return self.state.get(key, default)
    def set_state(self, key, val):
        self.state[key] = val
    def get_all_state(self):
        return self.state
    def xadd(self, stream, data, maxlen=None):
        pass
    def acquire_trading_lock(self, symbol, cooldown=30):
        return True

def generate_tick_data(symbol="EURUSD", count=100):
    ticks = []
    base_price = 1.1000
    current_time = time.time()
    for i in range(count):
        ticks.append([base_price, base_price + 0.0001, base_price - 0.0001, base_price, current_time + i, 10])
    return {"t": "DP", "type": "MARKET_DATA_RAW", "s": symbol, "b": base_price, "a": base_price + 0.0001, "tf": 1, "ltf": ticks, "h1": ticks, "h4": ticks, "atr": 0.0010}

@pytest.mark.asyncio
async def test_brain_v1_deep_flow():
    mock_ipc = MockIPC()
    md_brain = MarketDataBrain("MarketData", ipc=mock_ipc)
    tick_data = generate_tick_data()
    event = await md_brain.process(tick_data)
    assert event["type"] == "MARKET_DATA"
    assert mock_ipc.get_state("symbol_stats:EURUSD")["bid"] == 1.1

@pytest.mark.asyncio
async def test_meta_brain_confluence_logic():
    mock_ipc = MockIPC()
    # threshold 0.5 to make it easy to trigger in test
    meta = MetaBrain("MetaTest", threshold=0.50, ipc=mock_ipc)
    meta.required_sources = ["Trend_1", "Indicator_1"]

    # Evidence 1: Trend alignment (BULLISH)
    await meta.process({"symbol": "EURUSD", "type": "EVIDENCE", "source": "Trend_1", "p_e_h": 0.85, "p_e": 0.45, "direction": 1})

    # Evidence 2: Indicator alignment (BULLISH)
    result = await meta.process({"symbol": "EURUSD", "type": "EVIDENCE", "source": "Indicator_1", "p_e_h": 0.85, "p_e": 0.45, "direction": 1})

    assert result is not None
    assert result["type"] == "PROBABILISTIC_SIGNAL"
    assert result["action"] == "BUY"
    assert result["lots"] == 0.01
