import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorAnalyst:
    def __init__(self):
        """Magic: 8100"""
        self.magic = 8100

    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Magic: 8101"""
        if df.empty: return {"rsi": 50.0, "atr": 0.0, "m_id": 8101}
        return {
            "rsi": self.rsi(df['c']),
            "atr": self.atr(df),
            "m_id": 8101
        }

    def rsi(self, series: pd.Series, period: int = 14) -> float:
        """Magic: 8102"""
        if len(series) < period: return 50.0
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        loss = loss.replace(0, 1e-9)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Magic: 8103"""
        if len(df) < period: return 0.0
        high = df['h']; low = df['l']; close = df['c']
        tr = np.maximum(high - low, np.maximum(np.abs(high - close.shift(1)), np.abs(low - close.shift(1))))
        atr = tr.rolling(window=period).mean()
        return float(atr.iloc[-1])
