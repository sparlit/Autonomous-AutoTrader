import pytest
from src.python.brains.consensus import MetaBrain
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config
from multiprocessing import Queue

@pytest.mark.asyncio
async def test_meta_brain_logic():
    q = Queue()
    engine = MetaBrain("Meta", q, q)
    await engine.process({"symbol": "EURUSD", "type": "REGIME", "regime": "NORMAL"})
    await engine.process({"symbol": "EURUSD", "type": "TREND", "trend": "BULLISH"})
    await engine.process({"symbol": "EURUSD", "type": "INDICATORS", "indicators": {"atr": 0.01}})
    res = await engine.process({"symbol": "EURUSD", "type": "LIQUIDITY", "order_blocks": [{"type": "BULLISH"}]})
    assert res["action"] == "BUY"

def test_risk_manager_session():
    rm = RiskManager(load_config())
    assert isinstance(rm.is_session_active(), bool)

def test_risk_validation():
    rm = RiskManager(load_config())
    rm.daily_trades = 10
    res = rm.validate_trade("EURUSD", "BUY", 1000.0, ignore_session=True)
    assert res["safe"] == False
