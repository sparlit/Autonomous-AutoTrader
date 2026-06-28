from typing import Any
import pandas as pd
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class TurtleBreakout(BaseBrain):
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20011

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Magic: 20011"""
        history = data.get("history", [])
        if not history or len(history) < 21: return None

        df = pd.DataFrame(history)
        high_20 = df['h'].rolling(20).max().iloc[-2]
        low_20 = df['l'].rolling(20).min().iloc[-2]

        direction = 0
        if df['c'].iloc[-1] > high_20: direction = 1
        elif df['c'].iloc[-1] < low_20: direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.7 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
