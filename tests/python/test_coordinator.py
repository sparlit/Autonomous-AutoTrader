import asyncio
import ujson as json
import pytest
from src.python.hive.coordinator import HiveCoordinator

@pytest.mark.asyncio
async def test_ping_pong():
    coordinator = HiveCoordinator()
    # Mock message
    response = await coordinator.handle_message("test_client", {"t": "PNG"})
    assert response == {"t": "PNG_ACK"}

@pytest.mark.asyncio
async def test_heartbeat():
    coordinator = HiveCoordinator()
    response = await coordinator.handle_message("test_client", {"t": "HB", "s": "EURUSD", "e": 1000.0})
    assert response == {"t": "HB_ACK"}
    assert "test_client" in coordinator.agent_states
    assert coordinator.agent_states["test_client"]["symbol"] == "EURUSD"
    assert coordinator.agent_states["test_client"]["equity"] == 1000.0
