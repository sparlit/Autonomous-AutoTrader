from typing import Any, Optional
from src.python.brains.base import BaseBrain, SignalPayload
import pandas as pd

class VSAMaster(BaseBrain):
    """
    Volume Spread Analysis (VSA) Strategy.
    Logic: Effort vs Result, Stopping Volume.
    Magic: 20501
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20501

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if not history or len(history) < 20: return None

        df = pd.DataFrame(history)
        last_v = df['v'].iloc[-1]; prev_v = df['v'].iloc[-2]
        spread = df['h'].iloc[-1] - df['l'].iloc[-1]

        avg_v = df['v'].rolling(20).mean().iloc[-1]

        direction = 0
        if last_v > 2 * avg_v and spread < (df['h'] - df['l']).rolling(20).mean().iloc[-1]:
            # Stopping volume - possible reversal
            close = df['c'].iloc[-1]; low = df['l'].iloc[-1]; high = df['h'].iloc[-1]
            if close > (low + high)/2: direction = 1
            else: direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.65 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
