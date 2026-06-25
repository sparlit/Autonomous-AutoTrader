import pytest
import asyncio
import ujson as json
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_concurrent_message_handling():
    # Use a fresh orchestrator
    orchestrator = HiveOrchestrator()
    # Ensure a fresh state for the test
    orchestrator.ipc._queues.clear()
    orchestrator._initialize_ipc_queues()

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

    tasks = [
        orchestrator.handle_client_message(f"agent_{i}", {"t": "DP", "s": symbol})
        for i, symbol in enumerate(symbols)
    ]

    responses = await asyncio.gather(*tasks)
    assert len(responses) == len(symbols)

    total_messages = 0
    for stream in orchestrator.brain_inputs["MarketData"]:
        q = orchestrator._get_queue(stream)
        total_messages += q.qsize()

    assert total_messages == len(symbols)
