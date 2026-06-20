import logging
from typing import List, Optional
from src.python.brains.base import BaseBrain, SignalPayload

logger = logging.getLogger("AAT_SequentialBrain")

class SequentialBrain:
    def __init__(self, strategies: List[BaseBrain]):
        """
        Initialize a sequential brain with an ordered list of strategies.
        
        Parameters:
            strategies (List[BaseBrain]): Ordered list of strategies to execute sequentially.
        """
        self.strategies = strategies

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """
        Execute strategies sequentially and return the first matching signal.
        
        Iterates through each strategy, invoking its process method with the provided data.
        Returns the first signal with non-zero direction. If a strategy raises an exception,
        the error is logged and processing continues with the next strategy.
        
        Parameters:
            data (dict): Data to process through each strategy.
        
        Returns:
            SignalPayload or None: The first signal with non-zero direction, or None if no
            matching signal is found.
        """
        for strategy in self.strategies:
            try:
                signal = await strategy.process(data)
                if signal and signal.direction != 0:
                    logger.info(f"Sequential Match: {signal.strategy_name} -> {signal.direction}")
                    return signal
            except Exception as e:
                logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}")
        return None
