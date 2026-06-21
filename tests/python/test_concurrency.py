import pytest
import asyncio
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_concurrent_message_handling():
    orchestrator = HiveOrchestrator()
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

    tasks = [
        orchestrator.handle_client_message(f"agent_{i}", {"t": "DP", "s": symbol})
        for i, symbol in enumerate(symbols)
    ]

    responses = await asyncio.gather(*tasks)
    assert len(responses) == len(symbols)

    # Verify messages are across MarketData streams
    total_messages = 0
    for stream in orchestrator.brain_inputs["MarketData"]:
        msgs = orchestrator.redis.xread({stream: '0'}, count=10)
        if msgs:
            total_messages += len(msgs[0][1])
    assert total_messages == len(symbols)
