import logging
from typing import List, Optional, Dict, Any
from src.python.brains.base import BaseBrain, SignalPayload

class SequentialBrain(BaseBrain):
    def __init__(self, strategies: List[BaseBrain]):
        """Magic: 1501"""
        super().__init__("Sequential_Brain")
        self.strategies = strategies
        self.magic = 1501

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Magic: 1502"""
        # Sequential processing - first non-neutral signal wins (Veto/Priority model)
        for strategy in self.strategies:
            signal = await strategy.process(data)
            if signal and signal.direction != 0:
                return signal
        return None
