from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class ADXTrend(BaseBrain):
    async def process(self, data: dict) -> Optional[SignalPayload]:
        return SignalPayload(
            symbol=data.get("symbol", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=0, # Mock NEUTRAL
            confidence=0.0,
            strategy_name="ADX_Trend"
        )
