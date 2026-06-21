import pytest
import time
from src.python.brains.consensus import MetaBrain
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

def test_meta_brain_logic():
    engine = MetaBrain()
    # Populate indicators for a symbol
    engine.process_event({
        "type": "INDICATORS",
        "symbol": "EURUSD",
        "indicators": {"atr": 0.0010, "rsi": 50}
    })
    # Set Trend
    engine.process_event({
        "type": "TREND",
        "symbol": "EURUSD",
        "trend": "BULLISH",
        "sweep": "NONE"
    })
    # Trigger Liquidity
    result = engine.process_event({
        "type": "LIQUIDITY",
        "symbol": "EURUSD",
        "order_blocks": [{"type": "BULLISH"}]
    })
    assert result["action"] == "BUY"

def test_risk_manager_session():
    rm = RiskManager(load_config())
    assert isinstance(rm.is_session_active(), bool)

def test_risk_validation():
    rm = RiskManager(load_config())
    rm.daily_trades = 10
    res = rm.validate_trade("EURUSD", "BUY", 1000.0, ignore_session=True)
    assert res["safe"] == False
