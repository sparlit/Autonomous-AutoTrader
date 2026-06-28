from typing import Any
import pandas as pd
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class DonchianBreakout(BaseBrain):
    """
    Standard Donchian Channel breakout strategy.
    FOSS Strategy Implementation.
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20004

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Magic: 20004"""
        history = data.get("history", [])
        if not history or len(history) < 20: return None

        df = pd.DataFrame(history)
        upper = df['h'].rolling(20).max().iloc[-2]
        lower = df['l'].rolling(20).min().iloc[-2]

        direction = 0
        if df['c'].iloc[-1] > upper: direction = 1
        elif df['c'].iloc[-1] < lower: direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.6 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
