import pytest
import asyncio
import time
from unittest.mock import MagicMock
from src.python.hive.coordinator import HiveCoordinator

@pytest.mark.asyncio
async def test_ohlc_to_signal_flow():
    coordinator = HiveCoordinator()

    # Mock risk manager to avoid VETO during test
    coordinator.risk_manager.is_session_active = MagicMock(return_value=True)
    coordinator.risk_manager.is_news_safe = MagicMock(return_value=True)

    # Mock OHLC data (Data Push protocol)
    # The new Brain expects 'history' for consensus parsing
    ohlc_msg = {
        "t": "DP",
        "s": "EURUSD",
        "history": [[1.0, 1.1, 0.9, 1.0, 100, 10] for _ in range(50)],
        "ltf": [[1.0, 1.1, 0.9, 1.0, 100, 10] for _ in range(20)],
        "h1": [[1.0, 1.1, 0.9, 1.0, 100, 10] for _ in range(20)],
        "h4": [[1.0, 1.1, 0.9, 1.0, 100, 10] for _ in range(20)],
        "bi": 1.0,
        "as": 1.0001
    }

    # Agent must be in states for equity/drawdown calculation
    coordinator.agent_states["agent_1"] = {"symbol": "EURUSD", "equity": 1000.0, "last_seen": time.time()}

    response = await coordinator.handle_message("agent_1", ohlc_msg)

    # Check that a decision was returned
    assert response["t"] == "DEC"
    assert "act" in response
    # 'tlm' should be present if not VETOed
    assert "tlm" in response

@pytest.mark.asyncio
async def test_coordinator_init():
    coordinator = HiveCoordinator()
    assert coordinator.registry is not None
    assert coordinator.risk_manager is not None
