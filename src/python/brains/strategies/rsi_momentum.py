import pandas as pd
from src.python.analyst.indicators import IndicatorAnalyst

class RSIMomentum:
    def __init__(self):
        self.analyst = IndicatorAnalyst()

    def calculate_signal(self, df: pd.DataFrame) -> int:
        """Calculate signal based on RSI momentum."""
        if df.empty: return 0
        rsi = self.analyst.calculate_rsi(df).iloc[-1]
        if rsi > 60: return 1
        if rsi < 40: return -1
        return 0
