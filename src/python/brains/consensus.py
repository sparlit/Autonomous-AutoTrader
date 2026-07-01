import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
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
        self.required_sources = ["Trend_1", "Indicator_1", "Liquidity_1", "Regime_1"]

    async def initialize(self):
        await super().initialize()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None
        if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
        state = self.symbol_state[symbol]; e_type = event.get("type")

        if e_type == "MARKET_DATA_REFRESH": self.symbol_state[symbol] = self._new_state(); return None
        if e_type == "RELIABILITY_REPORT": self.brain_reliability = event.get("scores", {}); return None

        if e_type == "REGIME_STATUS":
            state["regime"] = event["regime"]
            state["received_sources"].add(event["source"])
            state["confluence"]["volatility"] = 1 if "TRENDING" in event["regime"] else 0
        elif e_type == "MOMENTUM_STATUS":
            state["confluence"]["momentum"] = event.get("direction", 0)
            state["received_sources"].add(event["source"])
        elif e_type == "STRUCTURE_STATUS":
            state["confluence"]["structure"] = 1 if event.get("fvgs", 0) > 0 or event.get("idm") != "NONE" else 0
            state["structure_trigger"] = event.get("trigger", "NONE")
            state["received_sources"].add(event["source"])
        elif e_type in ["VETO", "NEWS_VETO"]:
            state["veto"] = True
            state["veto_reason"] = event.get("reason")
        elif e_type == "EVIDENCE":
            # Update confluence based on source
            src = event["source"]
            if "Trend" in src: state["confluence"]["trend"] = event.get("direction", 0)
            elif "Indicator" in src: state["confluence"]["momentum"] = event.get("direction", 0)
            elif "Liquidity" in src: state["confluence"]["structure"] = 1 if event.get("direction") != 0 else 0

            p_e_h = event.get("p_e_h", 0.50); p_e = event.get("p_e", 0.50)
            rel = self.brain_reliability.get(event["source"], 1.0)

            # 12601: Reliability-weighted evidence
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
                state["atr"] = event["data"].get("atr", state["atr"]); state["rsi"] = event["data"].get("rsi", state["rsi"])

            if len(state["evidence_trail"]) % 2 == 0:
                self.publish({
                    "type": "TELEMETRY",
                    "symbol": symbol,
                    "scr": state["prior"],
                    "htf": state["regime"]
                })

        # Check for Decision
        if all(src in state["received_sources"] for src in self.required_sources):
            # 10620: Signal Latching Logic
            # Check for existing positions via shared IPC trades
            active_trades = self.ipc.get_state("active_trades", [])
            if any(t['symbol'] == symbol for t in active_trades):
                logger.debug(f"Signal suppressed for {symbol}: Position already open.")
                return None

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
                valid_trigger = True
                if state.get("structure_trigger") != "NONE":
                    if action == "BUY" and "BULLISH" not in state["structure_trigger"]: valid_trigger = False
                    if action == "SELL" and "BEARISH" not in state["structure_trigger"]: valid_trigger = False

                if valid_trigger:
                    res = {
                        "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": action,
                        "probability": state["prior"], "regime": state["regime"], "atr": state["atr"], "rsi": state["rsi"],
                        "confluence": agreement_count,
                        "evidence_trail": state["evidence_trail"],
                        "explainability": [f"{e['source']} ({e['reliability']:.2f}): {'+' if e['impact'] >= 0 else ''}{e['impact']:.2f} -> P={e['posterior']:.2f}" for e in state['evidence_trail']]
                    }
                    self.symbol_state[symbol] = self._new_state()
                    return res
        return None

    def _new_state(self):
        return {
            "prior": 0.50, "evidence_trail": [], "regime": "NORMAL", "veto": False,
            "received_sources": set(), "atr": 0.0, "rsi": 50,
            "confluence": {"trend": 0, "momentum": 0, "structure": 0, "volatility": 0},
            "structure_trigger": "NONE"
        }

    def _determine_direction(self, state):
        directions = [e["direction"] for e in state["evidence_trail"] if e["direction"] != 0]
        if not directions: return "WAIT"
        net_dir = sum(directions); return "BUY" if net_dir > 0 else ("SELL" if net_dir < 0 else "WAIT")
