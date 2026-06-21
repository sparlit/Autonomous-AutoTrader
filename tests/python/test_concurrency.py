import pytest
import asyncio
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_concurrent_message_handling():
    orchestrator = HiveOrchestrator()
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

    # Simulate concurrent messages from multiple agents
    tasks = [
        orchestrator.handle_client_message(f"agent_{i}", {"t": "DP", "s": symbol})
        for i, symbol in enumerate(symbols)
    ]

    responses = await asyncio.gather(*tasks)

    assert len(responses) == len(symbols)
    for resp in responses:
        assert resp["t"] == "ACK"

    # Check that all messages are in the queues
    total_queued = sum(q.qsize() for q in orchestrator.brain_inputs["MarketData"])
    assert total_queued == len(symbols)
