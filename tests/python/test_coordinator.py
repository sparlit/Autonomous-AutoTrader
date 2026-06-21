import pytest
import asyncio
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = HiveOrchestrator()
    assert orchestrator.registry is not None
    assert orchestrator.meta_brain is not None
    assert "MarketData" in orchestrator.brain_inputs
    assert len(orchestrator.brain_inputs["MarketData"]) == 2

@pytest.mark.asyncio
async def test_bridge_handling():
    orchestrator = HiveOrchestrator()
    msg = {"t": "DP", "s": "EURUSD"}
    response = await orchestrator.handle_client_message("test_client", msg)
    assert response["t"] == "ACK"

    # Verify message was queued in one of the MarketData queues
    found = False
    for q in orchestrator.brain_inputs["MarketData"]:
        # We don't check q.empty() because it can be unreliable, we just try to get with a small timeout
        try:
            queued_msg = q.get(timeout=0.1)
            if queued_msg == msg:
                found = True
                break
        except:
            continue
    assert found
