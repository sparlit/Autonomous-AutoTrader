import numpy as np
import pandas as pd
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class ADXTrend(BaseBrain):
    def __init__(self, name: str):
        super().__init__(name)
        self.magic = 2001

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """
        Analyze ADX Trend logic using vectorized computation.
        """
        history = data.get("history", [])
        if not history or len(history) < 30:
            return None

        df = pd.DataFrame(history)
        high = df['h']; low = df['l']; close = df['c']

        tr = np.maximum(high[1:] - low[1:],
                        np.maximum(np.abs(high[1:] - close[:-1]),
                                   np.abs(low[1:] - close[:-1])))

        up_move = high[1:].values - high[:-1].values
        down_move = low[:-1].values - low[1:].values

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        atr_14 = pd.Series(tr).rolling(14).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / atr_14)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / atr_14)

        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean().iloc[-1]

        direction = 0
        confidence = 0.0

        if adx > 25:
            if plus_di.iloc[-1] > minus_di.iloc[-1]:
                direction = 1
                confidence = min(1.0, adx / 50.0)
            elif minus_di.iloc[-1] > plus_di.iloc[-1]:
                direction = -1
                confidence = min(1.0, adx / 50.0)

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=confidence,
            strategy_name=self.name,
            magic=self.magic
        )
