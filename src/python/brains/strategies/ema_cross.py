from typing import Optional, Dict, Any
import pandas as pd
from src.python.brains.base import BaseBrain, SignalPayload

class EMACross(BaseBrain):
    """
    10201: EMA Crossover Strategy.
    Logic: EMA8 crossing EMA21.
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20005

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if len(history) < 30: return None
        df = pd.DataFrame(history)
        ema8 = df['c'].ewm(span=8).mean().iloc[-1]
        ema21 = df['c'].ewm(span=21).mean().iloc[-1]
        direction = 1 if ema8 > ema21 else -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.6,
            strategy_name=self.name,
            magic=self.magic
        )
