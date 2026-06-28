import pandas as pd
from typing import Any, Optional
from src.python.brains.base import BaseBrain, SignalPayload

class WyckoffMaster(BaseBrain):
    """
    10205: Wyckoff Methodology Strategy.
    Logic: Accumulation/Distribution phases, Spring/Upthrust detection.
    Magic: 20013
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20013

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20902"""
        history = data.get("history", [])
        if len(history) < 50: return None
        df = pd.DataFrame(history)
        if isinstance(history[0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

        # Simple Spring Detection: Price dips below recent low and closes back above
        recent_low = df['l'].iloc[-20:-1].min()
        last_low = df['l'].iloc[-1]
        last_close = df['c'].iloc[-1]

        direction = 0
        confidence = 0.0

        if last_low < recent_low and last_close > recent_low:
            direction = 1 # Spring (Bullish)
            confidence = 0.75

        recent_high = df['h'].iloc[-20:-1].max()
        last_high = df['h'].iloc[-1]

        if last_high > recent_high and last_close < recent_high:
            direction = -1 # Upthrust (Bearish)
            confidence = 0.75

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=confidence,
            strategy_name=self.name,
            magic=self.magic
        )
