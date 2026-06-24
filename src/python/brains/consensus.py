import asyncio
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Bayesian Probability Engine.
    Implements the "3 of 4" confluence rule: Trend, Momentum, Structure, Volatility.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.70, ipc: Any = None):
        super().__init__(name, cpu_affinity, ipc=ipc)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.brain_reliability: Dict[str, float] = {}
        self.required_sources = ["Trend_1", "Indicator_1", "Liquidity_1", "Regime_1", "Momentum_1", "Structure_1"]
        self._last_telemetry_broadcast = 0

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None
        if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
        state = self.symbol_state[symbol]; e_type = event.get("type")

        if e_type == "MARKET_DATA_REFRESH":
            state["received_sources"] = set()
            state["confluence"] = {"trend": 0, "momentum": 0, "structure": 0, "volatility": 0}
            return None

        if e_type == "RELIABILITY_REPORT":
            self.brain_reliability = event.get("scores", {})
            return None

        if e_type == "REGIME_STATUS":
            state["regime"] = event["regime"]
            state["received_sources"].add(event["source"])
            state["confluence"]["volatility"] = 1 if "TRENDING" in event["regime"] else 0

        elif e_type == "MOMENTUM_STATUS":
            state["confluence"]["momentum"] = event.get("direction", 0)
            state["received_sources"].add(event["source"])

        elif e_type == "STRUCTURE_STATUS":
            state["structure_trigger"] = event.get("trigger")
            state["confluence"]["structure"] = 1 if event.get("fvgs", 0) > 0 or event.get("idm") != "NONE" else 0
            state["received_sources"].add(event["source"])

        elif e_type in ["VETO", "NEWS_VETO"]:
            state["veto"] = True
            state["veto_reason"] = event.get("reason")

        elif e_type == "EVIDENCE":
            p_e_h = event.get("p_e_h", 0.50); p_e = event.get("p_e", 0.50)
            rel = self.brain_reliability.get(event["source"], 1.0)

            if "Trend" in event["source"]:
                state["confluence"]["trend"] = event.get("direction", 0)
                state["htf_trend"] = "BULLISH" if event.get("direction", 0) > 0 else "BEARISH" if event.get("direction", 0) < 0 else "NEUTRAL"

            weighted_p_e_h = 0.50 + (p_e_h - 0.50) * rel
            prior = state["prior"]; posterior = (weighted_p_e_h * prior) / p_e
            impact = posterior - prior
            state["prior"] = max(0.01, min(0.99, posterior))

            state["evidence_trail"].append({
                "source": event["source"],
                "direction": event.get("direction", 0),
                "posterior": state["prior"],
                "impact": impact,
                "reliability": rel
            })
            state["received_sources"].add(event["source"])

            if "data" in event:
                state["atr"] = event["data"].get("atr", state["atr"])
                state["rsi"] = event["data"].get("rsi", state["rsi"])

        # 10605: Broadcast Telemetry on every update for real-time dashboards
        acc_stats = self.ipc.get_state("account_stats", {}) if self.ipc else {}
        telemetry = {
            "type": "TELEMETRY",
            "symbol": symbol,
            "st": "OPTIMAL",
            "scr": round(state["prior"], 4),
            "htf": state["htf_trend"],
            "dd": acc_stats.get("drawdown", 0.0)
        }
        self.publish(telemetry)

        # Final Decision Logic
        if all(src in state["received_sources"] for src in self.required_sources):
            conf = state["confluence"]
            action = self._determine_direction(state)
            if action == "WAIT": return None

            bias = 1 if action == "BUY" else -1
            agreement_count = 0
            if conf["trend"] == bias: agreement_count += 1
            if conf["momentum"] == bias: agreement_count += 1
            if conf["structure"] == 1: agreement_count += 1
            if conf["volatility"] == 1: agreement_count += 1

            if agreement_count >= 3 and state["prior"] >= self.threshold and not state["veto"]:
                if state.get("structure_trigger") != "NONE" and action in state.get("structure_trigger", ""):
                    res = {
                        "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": action,
                        "probability": state["prior"], "regime": state["regime"], "atr": state["atr"], "rsi": state["rsi"],
                        "evidence_trail": list(state["evidence_trail"]),
                        "explainability": [f"{e['source']} ({e['reliability']:.2f}): impact {e['impact']:.2f}" for e in state['evidence_trail']]
                    }
                    self.symbol_state[symbol] = self._new_state()
                    return res
        return None

    def _new_state(self):
        return {
            "prior": 0.50,
            "evidence_trail": [],
            "regime": "NORMAL",
            "veto": False,
            "received_sources": set(),
            "atr": 0.0,
            "rsi": 50,
            "htf_trend": "NEUTRAL",
            "confluence": {"trend": 0, "momentum": 0, "structure": 0, "volatility": 0},
            "structure_trigger": "NONE"
        }

    def _determine_direction(self, state):
        directions = [e["direction"] for e in state["evidence_trail"] if e["direction"] != 0]
        if not directions: return "WAIT"
        net_dir = sum(directions); return "BUY" if net_dir > 0 else ("SELL" if net_dir < 0 else "WAIT")
