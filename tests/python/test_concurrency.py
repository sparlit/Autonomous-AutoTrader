import asyncio
import ujson as json
import pytest
from src.python.hive.coordinator import HiveCoordinator

@pytest.mark.asyncio
async def test_concurrent_clients():
    coordinator = HiveCoordinator()
    server_task = asyncio.create_task(coordinator.run())
    await asyncio.sleep(1)

    async def client_task(i):
        """
        Simulate a client connecting to the server, sending a PING message, and reading the response.
        
        Parameters:
        	i (int): Client identifier included in the PING message.
        
        Returns:
        	dict: Parsed JSON response from the server.
        """
        reader, writer = await asyncio.open_connection('127.0.0.1', 5555)
        writer.write(json.dumps({"type": "PING", "id": i}).encode() + b'\n')
        await writer.drain()
        data = await reader.readuntil(b'\n')
        writer.close()
        await writer.wait_closed()
        return json.loads(data.decode().strip())

    results = await asyncio.gather(*[client_task(i) for i in range(10)])
    assert len(results) == 10
    for res in results:
        assert res["type"] == "PONG"

    server_task.cancel()
