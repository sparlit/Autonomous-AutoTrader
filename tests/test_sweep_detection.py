import pytest
import pandas as pd
from src.python.analyst.price_action import SMCAnalyst

def test_liquidity_sweep():
    smc = SMCAnalyst()
    data = {"h": [1.0]*20, "l": [0.9]*20, "c": [0.95]*20, "o": [0.95]*20}
    df = pd.DataFrame(data)
    res = smc.detect_market_structure(df)
    assert "sweep" in res

def test_dynamic_pip_value():
    from src.python.execution.risk_manager import RiskManager
    from src.python.hive.config import load_config
    config = load_config()
    rm = RiskManager(config)
    # Risk 100 / (100 ticks * 1.0 val) = 1.0 lot
    params = rm.calculate_trade_params(
        equity=10000.0, atr=0.0050, symbol="EURUSD", action="BUY",
        tick_val=1.0, tick_size=0.0001
    )
    assert params["lots"] == 1.0
