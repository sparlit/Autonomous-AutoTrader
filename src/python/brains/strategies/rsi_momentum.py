from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class RSIMomentum(BaseBrain):
    async def process(self, data: dict) -> Optional[SignalPayload]:
        return SignalPayload(
            symbol=data.get("symbol", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=-1, # Mock SELL
            confidence=0.6,
            strategy_name="RSI_Momentum"
        )
