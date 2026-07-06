import pytest
import asyncio
import time
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = HiveOrchestrator()
    assert orchestrator.ipc is not None
    assert orchestrator.registry is not None
    assert orchestrator.server is not None
    assert orchestrator.ledger is not None
    assert orchestrator.risk_manager is not None
    assert orchestrator.pos_manager is not None

@pytest.mark.asyncio
async def test_bridge_handling():
    orchestrator = HiveOrchestrator()
    # Mock some expected state
    orchestrator.ipc.create_stream("stream:MarketData_1")

    msg = {"t": "DP", "s": "EURUSD", "tf": 1, "bi": 1.08, "as": 1.0801}
    response = await orchestrator.handle_bridge_message("test_client", msg)
    assert response["t"] == "ACK"

    # Check IPC stream for orchestrator
    messages = orchestrator.ipc.xread({"stream:orchestrator": '0'}, count=1)
    assert len(messages) > 0
