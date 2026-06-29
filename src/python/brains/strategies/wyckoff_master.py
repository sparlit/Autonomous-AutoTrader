from typing import Any, Optional
from src.python.brains.base import BaseBrain, SignalPayload
import pandas as pd

class WyckoffMaster(BaseBrain):
    """
    Wyckoff Theory Strategy.
    Logic: Accumulation/Distribution phases, Spring/Upthrust detection.
    Magic: 20601
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20601

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if not history or len(history) < 50: return None

        df = pd.DataFrame(history)
        # Simplified Spring/Upthrust detection
        rolling_min = df['l'].rolling(40).min().iloc[-2]
        rolling_max = df['h'].rolling(40).max().iloc[-2]

        last_low = df['l'].iloc[-1]
        last_high = df['h'].iloc[-1]
        last_close = df['c'].iloc[-1]

        direction = 0
        if last_low < rolling_min and last_close > rolling_min:
            direction = 1 # Spring
        elif last_high > rolling_max and last_close < rolling_max:
            direction = -1 # Upthrust

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.75 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
