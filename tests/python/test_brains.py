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
    return {"t": "DP", "s": symbol, "bi": base_price, "as": base_price + 0.0001, "tf": 1, "ltf": ticks, "h1": ticks, "h4": ticks}

@pytest.mark.asyncio
async def test_brain_v1_deep_flow():
    orchestrator = HiveOrchestrator()
    tick_data = generate_tick_data()
    md_brain = MarketDataBrain("MarketData")
    event = await md_brain.process(tick_data)
    assert event["type"] == "MARKET_DATA"

@pytest.mark.asyncio
async def test_meta_brain_bayesian_posterior():
    meta = MetaBrain("MetaTest", threshold=0.60)
    meta.required_sources = ["Trend_1", "Liquidity_1", "Regime_1"]

    # Evidence 1: Trend alignment
    await meta.process({"symbol": "EURUSD", "type": "EVIDENCE", "source": "Trend_1", "p_e_h": 0.85, "p_e": 0.45, "direction": 1})

    # Evidence 2: Volatility Regime
    await meta.process({"symbol": "EURUSD", "type": "REGIME_STATUS", "source": "Regime_1", "regime": "TRENDING_FAST"})

    # Evidence 3: Liquidity sweep (Triggers decision)
    result = await meta.process({"symbol": "EURUSD", "type": "EVIDENCE", "source": "Liquidity_1", "p_e_h": 0.80, "p_e": 0.60, "direction": 1})

    assert result is not None
    assert result["type"] == "PROBABILISTIC_SIGNAL"
    assert result["probability"] > 0.90
    assert result["action"] == "BUY"
    assert "explainability" in result
    assert "Trend_1" in result["explainability"][0]
