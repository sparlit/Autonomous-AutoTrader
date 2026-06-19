import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorAnalyst:
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "rsi": self.rsi(df['c']),
            "atr": self.atr(df),
            "ema_fast": df['c'].ewm(span=50, adjust=False).mean().iloc[-1],
            "ema_slow": df['c'].ewm(span=200, adjust=False).mean().iloc[-1]
        }

    def rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(window=period).mean()
        ma_down = down.rolling(window=period).mean()
        rs = ma_up / ma_down
        return (100 - (100 / (1 + rs))).iloc[-1]

    def atr(self, df: pd.DataFrame, period: int = 14) -> float:
        high = df['h']; low = df['l']; cp = df['c'].shift(1)
        tr = pd.concat([high-low, (high-cp).abs(), (low-cp).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]
