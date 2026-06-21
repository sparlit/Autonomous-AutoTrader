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

    found = False
    for q in orchestrator.brain_inputs["MarketData"]:
        try:
            queued_msg = q.get(timeout=0.1)
            if queued_msg == msg:
                found = True
                break
        except: continue
    assert found
