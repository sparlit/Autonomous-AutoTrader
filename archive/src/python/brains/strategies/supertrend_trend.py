from typing import Any
import pandas as pd
import numpy as np
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class SupertrendTrend(BaseBrain):
    """
    Institutional Supertrend implementation.
    FOSS Strategy Implementation.
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 2007

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Magic: 2007"""
        history = data.get("history", [])
        if not history or len(history) < 15: return None

        df = pd.DataFrame(history)
        high = df['h']; low = df['l']; close = df['c']

        tr = np.maximum(high - low, np.maximum(np.abs(high - close.shift(1)), np.abs(low - close.shift(1))))
        atr = tr.rolling(10).mean()

        multiplier = 3.0
        hl2 = (high + low) / 2
        upperband = hl2 + (multiplier * atr)
        lowerband = hl2 - (multiplier * atr)

        # Simplified trend logic
        direction = 1 if close.iloc[-1] > upperband.iloc[-1] else -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.7,
            strategy_name=self.name,
            magic=self.magic
        )
