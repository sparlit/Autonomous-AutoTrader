import pytest
import asyncio
import time
import pandas as pd
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
    md_brain = MarketDataBrain("MarketData")
    event = await md_brain.process(tick_data)
    assert event["type"] == "MARKET_DATA"

@pytest.mark.asyncio
async def test_meta_brain_scoring_and_explainability():
    meta = MetaBrain("MetaTest", threshold=70)
    await meta.process({"symbol": "EURUSD", "type": "REGIME", "regime": "TRENDING"})
    await meta.process({"symbol": "EURUSD", "type": "TREND", "trend": "BULLISH", "h1_trend": "BULLISH", "h4_trend": "BULLISH"})
    await meta.process({"symbol": "EURUSD", "type": "INDICATORS", "indicators": {"atr": 0.0010}})
    result = await meta.process({"symbol": "EURUSD", "type": "LIQUIDITY", "order_blocks": [{"type": "BULLISH"}]})
    assert result is not None
    assert result["action"] == "BUY"
    assert result["score"] == 90
    assert "H4 Aligned" in result["reasons"]

@pytest.mark.asyncio
async def test_meta_brain_explainability_detailed():
    meta = MetaBrain("MetaExplain", threshold=70)
    await meta.process({"symbol": "EURUSD", "type": "REGIME", "regime": "TRENDING"})
    await meta.process({
        "symbol": "EURUSD", "type": "TREND",
        "trend": "BULLISH", "m1_trend": "BULLISH", "m5_trend": "BULLISH",
        "h1_trend": "BULLISH", "h4_trend": "BULLISH"
    })
    await meta.process({"symbol": "EURUSD", "type": "INDICATORS", "indicators": {"atr": 0.0012, "rsi": 60}})
    result = await meta.process({"symbol": "EURUSD", "type": "LIQUIDITY", "order_blocks": [{"type": "BULLISH"}]})
    assert result is not None
    assert result["score"] == 100
    assert len(result["reasons"]) == 7
