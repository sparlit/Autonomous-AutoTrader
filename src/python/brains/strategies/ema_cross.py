from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class EMACross(BaseBrain):
    async def process(self, data: dict) -> Optional[SignalPayload]:
        # Dummy logic for Week 2 integration
        # In reality, this would use data['o'], data['h'], etc.
        return SignalPayload(
            symbol=data.get("symbol", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=1, # Mock BUY
            confidence=0.8,
            strategy_name="EMA_Cross"
        )
