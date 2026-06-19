import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorAnalyst:
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "rsi": self.rsi(df['c']),
            "atr": self.atr(df),
            "adx": self.adx(df),
            "ema_fast": df['c'].ewm(span=50).mean().iloc[-1],
            "ema_slow": df['c'].ewm(span=200).mean().iloc[-1]
        }

    def rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]

    def atr(self, df: pd.DataFrame, period: int = 14) -> float:
        tr = pd.concat([df['h'] - df['l'], (df['h'] - df['c'].shift()).abs(), (df['l'] - df['c'].shift()).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def adx(self, df: pd.DataFrame, period: int = 14) -> float:
        plus_dm = df['h'].diff().clip(lower=0)
        minus_dm = (df['l'].shift() - df['l']).clip(lower=0)
        tr = pd.concat([df['h'] - df['l'], (df['h'] - df['c'].shift()).abs(), (df['l'] - df['c'].shift()).abs()], axis=1).max(axis=1)

        atr_smooth = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr_smooth)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr_smooth)
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        return dx.rolling(period).mean().iloc[-1]
