import pytest
import asyncio
from src.python.hive.coordinator import HiveCoordinator

@pytest.mark.asyncio
async def test_ohlc_to_signal_flow():
    coordinator = HiveCoordinator()

    # Mock OHLC data
    ohlc_msg = {
        "type": "OHLC_PUSH",
        "symbol": "EURUSD",
        "tf": 60,
        "o": 1.0800,
        "h": 1.0850,
        "l": 1.0790,
        "c": 1.0840
    }

    response = await coordinator.handle_message("agent_1", ohlc_msg)

    # Check that a signal was generated (either by sequential or consensus)
    assert response["type"] == "SIGNAL"
    assert "direction" in response
    assert "strategy" in response

@pytest.mark.asyncio
async def test_consensus_logic():
    coordinator = HiveCoordinator()
    assert coordinator.sequential_brain is not None
    assert coordinator.consensus_brain is not None
    assert len(coordinator.registry.strategies) >= 3
