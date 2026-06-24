from typing import Optional, Dict, Any
import pandas as pd
from src.python.brains.base import BaseBrain, SignalPayload
from src.python.analyst.indicators import IndicatorAnalyst

class RSIMomentum(BaseBrain):
    """
    10202: RSI Momentum Strategy.
    Logic: RSI Overbought/Oversold levels with Trend filter.
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.analyst = IndicatorAnalyst()
        self.magic = 2002

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if len(history) < 30: return None
        df = pd.DataFrame(history)
        inds = self.analyst.calculate_all(df)
        rsi = inds["rsi"]

        direction = 0
        if rsi > 70: direction = -1 # Mean reversion Sell
        elif rsi < 30: direction = 1 # Mean reversion Buy

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.55 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
