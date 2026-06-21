import asyncio
import logging
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Meta Decision Engine.
    Aggregates signals from Trend, Indicators, Liquidity, Regime, and Veto brains.
    Produces Trade Quality Score and Explainability metadata.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 75.0):
        super().__init__(name, cpu_affinity)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None

        if symbol not in self.symbol_state:
            self.symbol_state[symbol] = {
                "trend": "NEUTRAL", "h1_trend": "NEUTRAL", "h4_trend": "NEUTRAL",
                "liquidity": False, "regime": "NEUTRAL", "indicators": {},
                "veto": False, "veto_reason": "", "m1_trend": "NEUTRAL", "m5_trend": "NEUTRAL"
            }

        e_type = event.get("type")
        state = self.symbol_state[symbol]

        if e_type == "TREND":
            state.update({
                "trend": event.get("trend", "NEUTRAL"),
                "h1_trend": event.get("h1_trend", "NEUTRAL"),
                "h4_trend": event.get("h4_trend", "NEUTRAL"),
                "m1_trend": event.get("m1_trend", "NEUTRAL"),
                "m5_trend": event.get("m5_trend", "NEUTRAL")
            })
        elif e_type == "INDICATORS":
            state["indicators"] = event["indicators"]
        elif e_type == "LIQUIDITY":
            state["liquidity"] = len(event.get("order_blocks", [])) > 0
        elif e_type == "REGIME":
            state["regime"] = event["regime"]
        elif e_type in ["VETO", "NEWS_VETO"]:
            state["veto"] = True; state["veto_reason"] = event.get("reason", "UNKNOWN_VETO")
        elif e_type == "MARKET_DATA_REFRESH":
            state["veto"] = False; state["veto_reason"] = ""
            return None

        # 10602: Multi-Timeframe Alignment & Scoring Logic
        if state["veto"]: return None

        # RUTHLESS RULE: H4 Trend MUST NOT be opposite to LTF Trend
        if state["h4_trend"] != "NEUTRAL" and state["trend"] != "NEUTRAL":
            if state["h4_trend"] != state["trend"]:
                return None # Hard Veto: Counter-Trend relative to H4

        score = 0
        reasons = []

        # 1. MTF Confirmation (Max 50 pts)
        if state["trend"] != "NEUTRAL":
            score += 10; reasons.append(f"Base Trend: {state['trend']}")
            # Alignments
            if state["trend"] == state["m1_trend"]: score += 5; reasons.append("M1 Aligned")
            if state["trend"] == state["m5_trend"]: score += 5; reasons.append("M5 Aligned")
            if state["trend"] == state["h1_trend"]: score += 15; reasons.append("H1 Aligned")
            if state["trend"] == state["h4_trend"]: score += 15; reasons.append("H4 Aligned")

        # 2. Liquidity (Max 30 pts)
        if state["liquidity"]: score += 30; reasons.append("Price at Order Block")

        # 3. Regime Optimization (Max 20 pts)
        if state["regime"] == "TRENDING": score += 20; reasons.append("Strong Trending Regime")
        elif state["regime"] == "NORMAL": score += 10; reasons.append("Stable Market Regime")
        elif state["regime"] == "HIGH_VOLATILITY": score -= 40; reasons.append("Excessive Volatility Veto")

        # 10603: Explainability Output
        if score >= self.threshold:
            action = "BUY" if state["trend"] == "BULLISH" else ("SELL" if state["trend"] == "BEARISH" else "WAIT")
            if action != "WAIT":
                # One-shot trigger per OB contact
                state["liquidity"] = False
                return {
                    "type": "SIGNAL",
                    "symbol": symbol,
                    "action": action,
                    "atr": state["indicators"].get("atr", 0.0),
                    "rsi": state["indicators"].get("rsi", 50),
                    "score": score,
                    "reasons": reasons
                }

        return None
