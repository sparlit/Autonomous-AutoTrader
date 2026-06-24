import pytest
import datetime
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

def test_news_safety_window():
    config = load_config()
    rm = RiskManager(config)
    now = datetime.datetime.now(datetime.UTC)
    event_time = (now + datetime.timedelta(minutes=15)).isoformat()
    # Updated to match the new 'name' and 'impact' requirements
    rm.news_events = [{"time": event_time, "name": "NFP", "impact": "High"}]
    assert rm.is_news_safe() == False

    event_time_far = (now + datetime.timedelta(minutes=45)).isoformat()
    rm.news_events = [{"time": event_time_far, "name": "FOMC", "impact": "High"}]
    assert rm.is_news_safe() == True

def test_atr_lot_sizing():
    config = load_config()
    rm = RiskManager(config)

    # Equity 10,000, 1% risk = 100
    # ATR 0.0050, SL Dist = 0.0100 (100 pips)
    # Default TickSize 0.0001, TickVal 10.0 (per 1.0 lot)
    # num_ticks = 0.0100 / 0.0001 = 100
    # lots = 100 / (100 * 10) = 0.1
    params = rm.calculate_trade_params(10000.0, 0.0050, "EURUSD", "BUY", tick_val=10.0, tick_size=0.0001)
    assert params["lots"] == 0.1
    assert params["sl_pts"] == 100
