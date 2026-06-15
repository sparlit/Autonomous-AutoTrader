import asyncio
import logging
from typing import List, Optional
from src.python.brains.base import BaseBrain, SignalPayload

logger = logging.getLogger("AAT_ConsensusBrain")

class ConsensusBrain:
    def __init__(self, strategies: List[BaseBrain], threshold: float = 0.7):
        self.strategies = strategies
        self.threshold = threshold

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Stage 2: Parallel weighted voting."""
        tasks = [strat.process(data) for strat in self.strategies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_signals: List[SignalPayload] = []
        for res in results:
            if isinstance(res, SignalPayload):
                valid_signals.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Strategy voting failed: {res}")

        if not valid_signals:
            return None

        total_score = 0.0
        # For Phase 1, weights are uniform. In Phase 2, these come from config.
        for sig in valid_signals:
            total_score += (sig.direction * sig.confidence)

        avg_score = total_score / len(self.strategies)

        if abs(avg_score) >= self.threshold:
            direction = 1 if avg_score > 0 else -1
            logger.info(f"Consensus Reached: {avg_score:.2f} -> {direction}")
            return SignalPayload(
                symbol=data.get("symbol", "UNKNOWN"),
                timeframe=data.get("tf", 0),
                direction=direction,
                confidence=abs(avg_score),
                strategy_name="ConsensusEngine",
                meta={"votes": len(valid_signals), "score": avg_score}
            )

        return None
