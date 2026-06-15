import asyncio
import ujson as json
import pytest
from src.python.hive.coordinator import HiveCoordinator

@pytest.mark.asyncio
async def test_ping_pong():
    coordinator = HiveCoordinator()
    # Mock message
    response = await coordinator.handle_message("test_client", {"type": "PING"})
    assert response == {"type": "PONG"}

@pytest.mark.asyncio
async def test_heartbeat():
    coordinator = HiveCoordinator()
    response = await coordinator.handle_message("test_client", {"type": "HEARTBEAT", "symbol": "EURUSD"})
    assert response == {"type": "HEARTBEAT_ACK"}
    assert "test_client" in coordinator.agent_states
    assert coordinator.agent_states["test_client"]["symbol"] == "EURUSD"

@pytest.mark.asyncio
async def test_bridge_echo():
    coordinator = HiveCoordinator()
    # Start server in background
    server_task = asyncio.create_task(coordinator.run())
    await asyncio.sleep(1) # Wait for server to start

    reader, writer = await asyncio.open_connection('127.0.0.1', 5555)

    # Send PING
    writer.write(json.dumps({"type": "PING"}).encode() + b'\n')
    await writer.drain()

    data = await reader.readuntil(b'\n')
    response = json.loads(data.decode().strip())
    assert response == {"type": "PONG"}

    writer.close()
    await writer.wait_closed()
    server_task.cancel()
