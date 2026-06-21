import pytest
import asyncio
import time
from typing import Dict, Any
from src.python.hive.coordinator import HiveCoordinator
from src.python.brains.consensus import ConsensusEngine

@pytest.fixture
def coordinator_sync():
    coord = HiveCoordinator()
    # Mock risk manager to allow all trades for deep testing
    coord.risk_manager.is_session_active = lambda: True
    coord.risk_manager.is_news_safe = lambda: True
    # Populate agent states
    coord.agent_states["deep_agent"] = {
        "symbol": "EURUSD",
        "equity": 10000.0,
        "last_seen": time.time()
    }
    return coord

def mock_ohlc(rows=100, price_base=1.0, drift=0.0001):
    return [[price_base + (i * drift), price_base + 0.0005 + (i * drift), price_base - 0.0005 + (i * drift), price_base + 0.0001 + (i * drift), 100+i, 10] for i in range(rows)]

@pytest.mark.asyncio
async def test_brain_v1_deep_tick_processing(coordinator_sync):
    """
    Test deep tick processing logic.
    Provides high-frequency simulated tick data to verify Brain consensus.
    """
    deep_msg = {
        "t": "DP",
        "s": "EURUSD",
        "history": mock_ohlc(50),
        "h1": mock_ohlc(10),
        "h4": mock_ohlc(5),
        "bi": 1.0000,
        "as": 1.0002,
        "tv": 10.0,
        "ts": 0.0001
    }

    response = await coordinator_sync.handle_message("deep_agent", deep_msg)

    assert response["t"] in ["DEC", "VETO"], f"Should return a Decision or Veto, got {response['t']}"

    if response["t"] == "DEC":
        assert "tlm" in response, "Decision must have telemetry"
        tlm = response["tlm"]
        assert "st" in tlm, "Telemetry must contain status"
        assert "scr" in tlm, "Telemetry must contain score"

@pytest.mark.asyncio
async def test_brain_v1_deep_consensus_convergence():
    """
    Verifies that the ConsensusEngine converges on a signal structure.
    """
    engine = ConsensusEngine()

    # Use named columns for history rows to avoid KeyError: 'c' in pandas
    raw_history = mock_ohlc(100)
    history_dicts = engine._parse_history(raw_history)

    consensus_data = {
        "s": "EURUSD",
        "history": history_dicts,
        "h1": engine._parse_history(mock_ohlc(20)),
        "h4": engine._parse_history(mock_ohlc(10)),
        "bi": 105.0,
        "as": 105.02,
        "tv": 10.0,
        "ts": 0.0001
    }

    result = engine.analyze_sync(consensus_data)

    assert "act" in result
    assert "scr" in result
    assert "m_id" in result
