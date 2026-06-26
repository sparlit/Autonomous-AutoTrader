# Version: V3.1.3-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
import logging
from typing import Dict, Any, List, Optional
from logic.base_brain import InstitutionalBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaConsensusBrain(InstitutionalBrain):
    """12300: Bayesian Aggregator for Multi-Brain signals."""
    def __init__(self, *args, threshold: float = 0.7, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.evidence: Dict[str, List[Dict[str, Any]]] = {}

    async def process(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # This brain listens to other brain outputs (signals)
        if msg.get('type') != 'SIGNAL': return None

        symbol = msg.get('symbol')
        if symbol not in self.evidence: self.evidence[symbol] = []

        self.evidence[symbol].append(msg)

        # Keep only last 5 signals for consensus
        if len(self.evidence[symbol]) > 5: self.evidence[symbol].pop(0)

        # Decision Logic: 3 of 4 or similar confluence
        buys = [s for s in self.evidence[symbol] if s['direction'] == 'BUY']
        sells = [s for s in self.evidence[symbol] if s['direction'] == 'SELL']

        if len(buys) >= 2:
            return {
                "type": "EXECUTION",
                "symbol": symbol,
                "act": "BUY",
                "confidence": len(buys) / 5.0
            }
        elif len(sells) >= 2:
            return {
                "type": "EXECUTION",
                "symbol": symbol,
                "act": "SELL",
                "confidence": len(sells) / 5.0
            }

        return None
