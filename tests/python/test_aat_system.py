import pytest
from src.python.brains.consensus import ConsensusEngine
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

def test_consensus_logic():
    engine = ConsensusEngine()
    data = {"history": [[1.0+i*0.01, 1.02+i*0.01, 0.99+i*0.01, 1.01+i*0.01, 1000+i, 100] for i in range(20)]}
    result = engine.analyze_sync(data)
    assert "act" in result

def test_risk_manager_session():
    rm = RiskManager(load_config())
    assert isinstance(rm.is_session_active(), bool)

def test_risk_validation():
    rm = RiskManager(load_config())
    rm.daily_trades = 10
    res = rm.validate_trade("EURUSD", "BUY", 1000.0, ignore_session=True)
    assert res["safe"] == False
