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

    async def process_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tasks = [brain.process(data) for brain in self._brains.values()]
        results = await asyncio.gather(*tasks)
        return {brain.name: result for brain, result in zip(self._brains.values(), results)}
