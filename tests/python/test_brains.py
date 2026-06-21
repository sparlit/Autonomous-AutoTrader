import pytest
import asyncio
import time
from multiprocessing import Queue
from src.python.hive.coordinator import HiveOrchestrator
from src.python.brains.specialized import MarketDataBrain

@pytest.mark.asyncio
async def test_brain_v1_deep_flow():
    """Test the deep flow of data through the new multi-process architecture."""
    orchestrator = HiveOrchestrator()

    # Mock data with tick-level precision
    tick_data = {
        "t": "DP",
        "s": "EURUSD",
        "bi": 1.1000,
        "as": 1.1001,
        "ltf": [[1.1000, 1.1005, 1.0995, 1.1002, time.time(), 100] for _ in range(100)]
    }

    # Push to first MarketData input queue
    orchestrator.brain_inputs["MarketData"][0].put(tick_data)

    # 1. MarketData Brain simulation
    md_brain = MarketDataBrain("MarketData", orchestrator.brain_inputs["MarketData"][0], orchestrator.brain_output_queue)
    # Manually run one process cycle
    event = await md_brain.process(tick_data)
    assert event["type"] == "MARKET_DATA"
    assert event["symbol"] == "EURUSD"

    # 2. Orchestrator Routing simulation
    for q in orchestrator.brain_inputs["Indicator"]: q.put(event)
    for q in orchestrator.brain_inputs["Trend"]: q.put(event)

    item = orchestrator.brain_inputs["Indicator"][0].get(timeout=1)
    assert item["type"] == "MARKET_DATA"

    item = orchestrator.brain_inputs["Trend"][0].get(timeout=1)
    assert item["symbol"] == "EURUSD"

@pytest.mark.asyncio
async def test_meta_brain_consensus():
    """Test that MetaBrain correctly aggregates signals."""
    from src.python.brains.consensus import MetaBrain
    meta = MetaBrain(threshold=0.7)

    # Simulate signals from different brains
    meta.process_event({"type": "TREND", "symbol": "EURUSD", "trend": "BULLISH", "sweep": "NONE"})
    meta.process_event({"type": "INDICATORS", "symbol": "EURUSD", "indicators": {"atr": 0.0010}})

    # This should trigger a BUY signal
    result = meta.process_event({"type": "LIQUIDITY", "symbol": "EURUSD", "order_blocks": [{"type": "BULLISH"}]})

    assert result is not None
    assert result["type"] == "SIGNAL"
    assert result["action"] == "BUY"
    assert result["atr"] == 0.0010
