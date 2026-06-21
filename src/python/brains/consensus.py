import asyncio
import logging
from typing import Dict, Any, List, Optional
from multiprocessing import Queue
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - The Meta Decision Engine.
    Receives signals from all specialized brains and produces a final decision.
    """
    def __init__(self, name: str, input_queue: Queue, output_queue: Queue, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.7):
        super().__init__(name, input_queue, output_queue, cpu_affinity)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None

        if symbol not in self.symbol_state:
            self.symbol_state[symbol] = {
                "trend": "NEUTRAL",
                "liquidity": False,
                "regime": "NEUTRAL",
                "indicators": {},
                "veto": False
            }

        e_type = event.get("type")

        if e_type == "TREND":
            self.symbol_state[symbol]["trend"] = event["trend"]
        elif e_type == "INDICATORS":
            self.symbol_state[symbol]["indicators"] = event["indicators"]
        elif e_type == "LIQUIDITY":
            self.symbol_state[symbol]["liquidity"] = len(event["order_blocks"]) > 0
        elif e_type == "REGIME":
            self.symbol_state[symbol]["regime"] = event["regime"]
        elif e_type in ["VETO", "NEWS_VETO"]:
            self.symbol_state[symbol]["veto"] = True
            logger.warning(f"MetaBrain VETO for {symbol}: {event.get('reason')}")
        elif e_type == "MARKET_DATA_REFRESH": # A way to reset vetoes
            self.symbol_state[symbol]["veto"] = False
            return None

        state = self.symbol_state[symbol]
        if state["veto"]: return None

        action = "WAIT"
        if state["regime"] != "HIGH_VOLATILITY":
            if state["trend"] == "BULLISH" and state["liquidity"]:
                action = "BUY"
            elif state["trend"] == "BEARISH" and state["liquidity"]:
                action = "SELL"

        if action != "WAIT":
            self.symbol_state[symbol]["liquidity"] = False
            return {
                "type": "SIGNAL",
                "symbol": symbol,
                "action": action,
                "atr": state["indicators"].get("atr", 0.0),
                "reasons": f"Trend:{state['trend']}, Regime:{state['regime']}, OB:True"
            }

        return None
