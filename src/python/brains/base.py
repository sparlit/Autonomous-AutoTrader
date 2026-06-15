from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class SignalPayload(BaseModel):
    symbol: str
    timeframe: int
    direction: int  # 1 for BUY, -1 for SELL, 0 for NEUTRAL
    confidence: float # 0.0 to 1.0
    strategy_name: str
    meta: Optional[dict] = None

class BaseBrain(ABC):
    @abstractmethod
    async def process(self, data: dict) -> Optional[SignalPayload]:
        pass
