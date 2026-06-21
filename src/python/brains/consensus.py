from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain:
    """
    The Meta Decision Engine.
    Receives signals from all brains, validates, weights, and produces final decisions.
    """
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}

    def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Aggregate brain outputs and check for consensus.
        """
        symbol = event.get("symbol")
        if not symbol: return None

        if symbol not in self.symbol_state:
            self.symbol_state[symbol] = {
                "trend": "NEUTRAL",
                "momentum": "NEUTRAL",
                "liquidity": False,
                "indicators": {}
            }

        e_type = event.get("type")

        if e_type == "TREND":
            self.symbol_state[symbol]["trend"] = event["trend"]
        elif e_type == "INDICATORS":
            self.symbol_state[symbol]["indicators"] = event["indicators"]
        elif e_type == "LIQUIDITY":
            # Check if price is near an order block
            self.symbol_state[symbol]["liquidity"] = len(event["order_blocks"]) > 0

        # Simple Consensus Logic
        state = self.symbol_state[symbol]
        action = "WAIT"

        if state["trend"] == "BULLISH" and state["liquidity"]:
            action = "BUY"
        elif state["trend"] == "BEARISH" and state["liquidity"]:
            action = "SELL"

        if action != "WAIT":
            # Reset state after signal to prevent duplicate triggers
            self.symbol_state[symbol]["liquidity"] = False
            return {
                "type": "SIGNAL",
                "symbol": symbol,
                "action": action,
                "atr": state["indicators"].get("atr", 0.0)
            }

        return None

