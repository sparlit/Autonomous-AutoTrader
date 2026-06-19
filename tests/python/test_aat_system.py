import pytest
import asyncio
from src.python.brains.consensus import ConsensusEngine
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

def test_consensus_logic():
    engine = ConsensusEngine()
    # History with clear uptrend
    data = {
        "history": [
            {"o": 1.0 + i*0.01, "h": 1.02 + i*0.01, "l": 0.99 + i*0.01, "c": 1.01 + i*0.01, "t": 1000 + i, "v": 100}
            for i in range(20)
        ]
    }
    result = engine.analyze_sync(data)
    assert "action" in result
    assert result["score"] >= 0 # Should be bullish or neutral

def test_risk_manager_session():
    config = load_config()
    rm = RiskManager(config)
    is_active = rm.is_session_active()
    assert isinstance(is_active, bool)

def test_risk_validation():
    config = load_config()
    rm = RiskManager(config)
    rm.daily_trades = 10
    res = rm.validate_trade("EURUSD", "BUY", 1000.0, ignore_session=True)
    assert res["safe"] == False
    assert res["reason"] == "Daily trade limit reached"
