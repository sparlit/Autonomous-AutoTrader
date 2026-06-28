import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
import ujson as json
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Bayesian Probability Engine.
    Implements a Bayesian Consensus logic across multiple specialized strategies.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.70, ipc: Any = None):
        super().__init__(name, cpu_affinity, ipc=ipc)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.strategy_reliability: Dict[str, float] = {}
        # 10602: Required sources for a valid consensus round
        self.required_sources: List[str] = []

    async def initialize(self):
        """10603: Initialize Bayesian Priors."""
        await super().initialize()
        # Initial reliability scores for strategies
        self.strategy_reliability = {
            "ScalpMaster": 1.0,
            "SwingMaster": 1.0,
            "ICTKillzone": 1.0,
            "ADXTrend": 1.0,
            "RSIMomentum": 1.0,
            "VSAMaster": 1.0,
            "WyckoffMaster": 1.0
        }

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """10604: Process incoming evidence and update posterior probability."""
        symbol = event.get("symbol") or event.get("s")
        if not symbol: return None

        if symbol not in self.symbol_state:
            self.symbol_state[symbol] = self._new_state()

        state = self.symbol_state[symbol]
        e_type = event.get("type") or event.get("t")

        # 10605: Handle Reliability Updates from MemoryBrain
        if e_type == "RELIABILITY_REPORT":
            self.strategy_reliability.update(event.get("scores", {}))
            return None

        # 10606: Handle Market Data Resets
        if e_type == "MARKET_DATA_REFRESH":
            self.symbol_state[symbol] = self._new_state()
            return None

        # 10610: Process Strategy Signals (SignalPayload / result from other brains)
        # Note: Strategy brains publish results to orchestrator, which are then routed to Meta_1
        src = event.get("strategy_name") or event.get("source")
        if src and src in self.strategy_reliability:
            direction = event.get("direction", 0)
            confidence = event.get("confidence", 0.0)

            if direction == 0: return None

            # Bayesian Update: Simplified to a weighted reliability update
            rel = self.strategy_reliability.get(src, 1.0)
            weighted_conf = confidence * rel

            state["votes"][src] = direction
            state["confidences"][src] = weighted_conf
            state["received_sources"].add(src)

            state["evidence_trail"].append({
                "source": src,
                "direction": direction,
                "confidence": confidence,
                "reliability": rel,
                "weighted_conf": weighted_conf
            })

            # 10615: Emit telemetry for dashboards
            self.publish({
                "type": "TELEMETRY",
                "symbol": symbol,
                "scr": state["prior"],
                "htf": "EVOLVING"
            })

        # 10620: Decision Logic - Triggered when sufficient strategies have voted
        # Or a timeout occurs (handled by orchestrator sending refresh)
        if len(state["received_sources"]) >= len(self.required_sources) and len(self.required_sources) > 0:
            final_direction = self._calculate_consensus(state)
            if final_direction == 0: return None

            # Calculate final probability
            prob = self._calculate_final_probability(state, final_direction)

            if prob >= self.threshold:
                action = "BUY" if final_direction > 0 else "SELL"
                res = {
                    "type": "PROBABILISTIC_SIGNAL",
                    "symbol": symbol,
                    "action": action,
                    "probability": prob,
                    "evidence_trail": state["evidence_trail"],
                    "atr": event.get("atr", 0.0)
                }
                # Reset state after decision
                self.symbol_state[symbol] = self._new_state()
                return res

        return None

    def _new_state(self):
        """10607: New symbol tracking state."""
        return {
            "prior": 0.50,
            "votes": {},
            "confidences": {},
            "received_sources": set(),
            "evidence_trail": [],
            "veto": False
        }

    def _calculate_consensus(self, state: Dict[str, Any]) -> int:
        """10621: Simple majority vote."""
        if not state["votes"]: return 0
        net_vote = sum(state["votes"].values())
        if net_vote > 0: return 1
        if net_vote < 0: return -1
        return 0

    def _calculate_final_probability(self, state: Dict[str, Any], direction: int) -> float:
        """10622: Probability based on matching confidence scores."""
        matching_confs = [c for src, c in state["confidences"].items() if state["votes"].get(src) == direction]
        if not matching_confs: return 0.0
        # Average matching confidence vs total possible sources
        return sum(matching_confs) / len(self.required_sources)
