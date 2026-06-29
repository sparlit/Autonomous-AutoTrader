import pytest
import asyncio
import time
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = HiveOrchestrator()
    assert orchestrator.registry is not None
    # Verify some brains are registered
    assert len(orchestrator.registry._brains) > 0

@pytest.mark.asyncio
async def test_bridge_handling():
    orchestrator = HiveOrchestrator()
    # 10265: Manually initialize test streams as test runner instance may differ
    orchestrator._initialize_ipc_queues()

    msg = {"t": "DP", "s": "EURUSD"}
    response = await orchestrator.handle_client_message("test_client", msg)
    assert response["t"] == "ACK"

    # Check IPC stream directly
    # MarketData messages are routed to MarketData_1 or MarketData_2
    found = False
    for stream in ["stream:MarketData_1", "stream:MarketData_2"]:
        # 10258: Use xread correctly with the new Queue-based IPC
        messages = orchestrator.ipc.xread({stream: '0'}, count=1)
        if messages:
            found = True
            break
    assert found
