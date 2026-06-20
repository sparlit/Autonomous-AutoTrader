import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseBrain(ABC):
    def __init__(self, name: str):
        """
        Initialize a brain with the given name.
        """
        self.name = name

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return the result.

        Parameters:
		data (Dict[str, Any]): The input data to process

        Returns:
		Dict[str, Any]: The processed output
        """
        pass

class BrainRegistry:
    def __init__(self):
        """Initialize an empty brain registry."""
        self._brains: Dict[str, BaseBrain] = {}

    def register(self, brain: BaseBrain):
        """
        Register a brain in the registry under its name.

        If a brain with the same name already exists, it will be replaced.
        """
        self._brains[brain.name] = brain

    async def process_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data through all registered brains concurrently and collect their results.

        Returns:
            Dict[str, Any]: Dictionary mapping each brain's name to its processed result
        """
        tasks = [brain.process(data) for brain in self._brains.values()]
        results = await asyncio.gather(*tasks)
        return {brain.name: result for brain, result in zip(self._brains.values(), results)}
