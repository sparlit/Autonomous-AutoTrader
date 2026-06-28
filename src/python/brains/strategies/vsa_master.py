import pandas as pd
from typing import Any, Optional
from src.python.brains.base import BaseBrain, SignalPayload
from src.python.analyst.volatility import VolatilityAnalyst

class VSAMaster(BaseBrain):
    """
    10204: Volume Spread Analysis (VSA) Strategy.
    Logic: Effort vs Result, Stopping Volume, No Demand.
    Magic: 20801
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.vol_analyst = VolatilityAnalyst()
        self.magic = 20801

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20802"""
        history = data.get("history", [])
        if len(history) < 20: return None
        df = pd.DataFrame(history)
        if isinstance(history[0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

        vsa = self.vol_analyst.analyze_vsa(df)

        direction = 0
        confidence = 0.0

        if vsa["effort"] == "HIGH" and vsa["result"] == "STRONG":
            direction = 1 if df['c'].iloc[-1] > df['o'].iloc[-1] else -1
            confidence = 0.7
        elif vsa["anomaly"] == "ABSORPTION":
            # Reversal potential
            direction = -1 if df['c'].iloc[-1] > df['o'].iloc[-1] else 1
            confidence = 0.65

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=confidence,
            strategy_name=self.name,
            magic=self.magic
        )
