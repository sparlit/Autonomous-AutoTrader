from src.python.analyst.price_action import SMCAnalyst
from src.python.brains.base import BaseBrain, SignalPayload
import pandas as pd
from typing import Optional

class ScalpMaster(BaseBrain):
    """
    M1 SMC Scalping Strategy.
    Logic: Liquidity Sweep + Reversal Candle.
    Magic: 20401
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.smc = SMCAnalyst()
        self.magic = 20401

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if not history or len(history) < 30: return None

        df = pd.DataFrame(history)
        struct = self.smc.detect_market_structure(df)
        trigger = self.smc.detect_candlestick_trigger(df)

        direction = 0
        if struct["sweep"] == "BULLISH_SWEEP" and trigger and "BULLISH" in trigger:
            direction = 1
        elif struct["sweep"] == "BEARISH_SWEEP" and trigger and "BEARISH" in trigger:
            direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.7 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
