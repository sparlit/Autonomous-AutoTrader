import asyncio
import logging
from typing import List, Optional, Dict, Any
from src.python.brains.base import BaseBrain, SignalPayload

class ConsensusBrain(BaseBrain):
    def __init__(self, strategies: List[BaseBrain], threshold: float = 0.7):
        """Magic: 1401"""
        super().__init__("Consensus_Brain")
        self.strategies = strategies
        self.threshold = threshold
        self.magic = 1401

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Magic: 1402"""
        tasks = [strat.process(data) for strat in self.strategies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        votes = []
        for res in results:
            if isinstance(res, SignalPayload):
                votes.append(res)
            elif isinstance(res, Exception):
                self.logger.error(f"Strategy voting failed: {res}")

        if not votes: return None

        # Aggregate logic
        total_direction = sum(v.direction for v in votes)
        avg_confidence = sum(v.confidence for v in votes) / len(votes)

        # Final decision
        final_direction = 0
        if total_direction >= (len(votes) * self.threshold): final_direction = 1
        elif total_direction <= -(len(votes) * self.threshold): final_direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=final_direction,
            confidence=avg_confidence,
            strategy_name=self.name,
            magic=self.magic
        )
