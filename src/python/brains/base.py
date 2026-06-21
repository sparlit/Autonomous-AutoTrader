import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class SignalPayload(BaseModel):
    symbol: str
    timeframe: int
    direction: int
    confidence: float
    strategy_name: str
    magic: int

class BaseBrain(ABC):
    def __init__(self, name: str):
        """Magic: 11001"""
        self.name = name
        self.logger = logging.getLogger(f"Brain_{self.name}")

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Any:
        """Subclasses MUST implement this."""
        raise NotImplementedError("Fatal: BaseBrain.process must be overridden.")

class BrainRegistry:
    def __init__(self):
        """Magic: 11002"""
        self._brains: Dict[str, BaseBrain] = {}

    def register(self, brain: BaseBrain):
        """Magic: 11003"""
        self._brains[brain.name] = brain
        logging.info(f"Registry: Registered {brain.name}")

    async def process_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 11004"""
        tasks = [brain.process(data) for brain in self._brains.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for brain, result in zip(self._brains.values(), results):
            if isinstance(result, Exception):
                logging.error(f"Brain {brain.name} failure: {result}")
                output[brain.name] = {"status": "ERROR", "msg": str(result)}
            else:
                output[brain.name] = result
        return output
