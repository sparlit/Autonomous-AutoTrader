import pytest
import asyncio
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = HiveOrchestrator()
    assert orchestrator.registry is not None
    assert "MarketData" in orchestrator.brain_inputs

@pytest.mark.asyncio
async def test_bridge_handling():
    orchestrator = HiveOrchestrator()
    msg = {"t": "DP", "s": "EURUSD"}
    response = await orchestrator.handle_client_message("test_client", msg)
    assert response["t"] == "ACK"

    # Check IPC stream directly
    found = False
    for stream in orchestrator.brain_inputs["MarketData"]:
        messages = orchestrator.ipc.xread({stream: '0'}, count=1)
        if messages:
            found = True
            break
    assert found
