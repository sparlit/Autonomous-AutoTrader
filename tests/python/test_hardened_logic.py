import pytest
import datetime
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

def test_news_safety_window():
    config = load_config()
    rm = RiskManager(config)

    # Event 15 minutes from now
    now = datetime.datetime.now(datetime.UTC)
    event_time = (now + datetime.timedelta(minutes=15)).isoformat()
    rm.news_events = [{"time": event_time, "event": "NFP"}]

    assert rm.is_news_safe() == False

    # Event 45 minutes from now
    event_time_far = (now + datetime.timedelta(minutes=45)).isoformat()
    rm.news_events = [{"time": event_time_far, "event": "FOMC"}]
    assert rm.is_news_safe() == True

def test_atr_lot_sizing():
    config = load_config()
    rm = RiskManager(config)

    # Equity 10,000, 1% risk = 100
    # Price 1.1000, ATR 0.0050 -> SL = 1.0900 (100 pips)
    # 100 risk / (100 pips * 10/pip) = 0.1 lots
    params = rm.calculate_trade_params(10000.0, 0.0050, "EURUSD", "BUY", 1.1000)
    assert params["lots"] == 0.1
    assert params["sl"] == 1.0900
    assert params["tp"] == 1.1200
