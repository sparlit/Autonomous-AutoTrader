import logging
from typing import List, Optional
from src.python.brains.base import BaseBrain, SignalPayload

logger = logging.getLogger("AAT_SequentialBrain")

class SequentialBrain:
    def __init__(self, strategies: List[BaseBrain]):
        self.strategies = strategies

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Stage 1: Linear execution. First match triggers."""
        for strategy in self.strategies:
            try:
                signal = await strategy.process(data)
                if signal and signal.direction != 0:
                    logger.info(f"Sequential Match: {signal.strategy_name} -> {signal.direction}")
                    return signal
            except Exception as e:
                logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}")
        return None
