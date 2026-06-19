<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/main
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseBrain(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class BrainRegistry:
    def __init__(self):
        self._brains: Dict[str, BaseBrain] = {}

    def register(self, brain: BaseBrain):
        self._brains[brain.name] = brain

    def get_brain(self, name: str) -> BaseBrain:
        return self._brains.get(name)

    async def process_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tasks = [brain.process(data) for brain in self._brains.values()]
        results = await asyncio.gather(*tasks)
        return {brain.name: result for brain, result in zip(self._brains.values(), results)}
<<<<<<< HEAD
=======
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
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
=======
>>>>>>> origin/main
