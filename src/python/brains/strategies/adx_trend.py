from typing import Optional, Dict, Any
import pandas as pd
from src.python.brains.base import BaseBrain, SignalPayload
from src.python.analyst.indicators import IndicatorAnalyst

class ADXTrend(BaseBrain):
    """
    10203: ADX Trend Strength Strategy.
    Logic: ADX > 25 indicates strong trend.
    Magic: 20001
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.analyst = IndicatorAnalyst()
        self.magic = 20001

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20602"""
        history = data.get("history", [])
        if len(history) < 30: return None
        df = pd.DataFrame(history)
        inds = self.analyst.calculate_all(df)
        adx = inds["adx"]

        direction = 0
        if adx > 25:
            # If ADX is high, we follow the EMA trend
            direction = 1 if df['c'].iloc[-1] > inds["ema_fast"] else -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.65 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
