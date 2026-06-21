import pytest
import asyncio
import time
import pandas as pd
from multiprocessing import Queue
from src.python.hive.coordinator import HiveOrchestrator
from src.python.brains.specialized import MarketDataBrain
from src.python.brains.consensus import MetaBrain

def generate_tick_data(symbol="EURUSD", count=100):
    ticks = []
    base_price = 1.1000
    current_time = time.time()
    for i in range(count):
        ticks.append([base_price, base_price + 0.0001, base_price - 0.0001, base_price, current_time + i, 10])
    return {"t": "DP", "s": symbol, "bi": base_price, "as": base_price + 0.0001, "ltf": ticks}

@pytest.mark.asyncio
async def test_brain_v1_deep_flow():
    orchestrator = HiveOrchestrator()
    tick_data = generate_tick_data()

    q_in = orchestrator.brain_inputs["MarketData"][0]
    q_out = orchestrator.output_queue
    md_brain = MarketDataBrain("MarketData", q_in, q_out)

    event = await md_brain.process(tick_data)
    assert event["type"] == "MARKET_DATA"

    # Push to Indicators
    orchestrator.brain_inputs["Indicator"][0].put(event)
    item = orchestrator.brain_inputs["Indicator"][0].get(timeout=1)
    assert item["type"] == "MARKET_DATA"

@pytest.mark.asyncio
async def test_meta_brain_consensus():
    q_in = Queue()
    q_out = Queue()
    meta = MetaBrain("MetaTest", q_in, q_out)

    # Simulate partial signals
    await meta.process({"symbol": "EURUSD", "type": "TREND", "trend": "BULLISH"})
    await meta.process({"symbol": "EURUSD", "type": "INDICATORS", "indicators": {"atr": 0.0010}})

    # Confirm with Liquidity
    result = await meta.process({"symbol": "EURUSD", "type": "LIQUIDITY", "order_blocks": [{"type": "BULLISH"}]})

    assert result is not None
    assert result["action"] == "BUY"
