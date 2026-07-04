import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
import json
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Bayesian Probability Engine (V3.3.0-ASCENDANT).
    Mandatory: MTF Trend Alignment, Consecutive Majority.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.70, ipc: Any = None):
        super().__init__(name, cpu_affinity, ipc=ipc)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.brain_reliability: Dict[str, float] = {}
        self.required_sources = ["Trend_1", "Indicator_1"] # Minimum viable for signal
        self.confluence_threshold = 3 # Default required agreement points

    async def initialize(self):
        await super().initialize()
        # 10610: Seed reliability from IPC if available
        self.brain_reliability = self.ipc.get_state("brain_reliability", {})
        asyncio.create_task(self._learning_loop())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            symbol = event.get("symbol")
            if not symbol: return None

            # Scaling Signal handling
            if event.get("scaling"):
                res = {
                    "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": event.get("action", "BUY"),
                    "probability": 0.95, "reason": "SCALING_ALIGNED", "scaling": True, "lots": 0.01
                }
                self.publish_state(symbol, {"mode": "SCALING", "action": res["action"], "prob": 0.95})
                return res

            if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
            state = self.symbol_state[symbol]; e_type = event.get("type")

            if e_type == "RELIABILITY_REPORT":
                self.brain_reliability = event.get("scores", {})
                if self.brain_reliability:
                    avg_rel = sum(self.brain_reliability.values()) / len(self.brain_reliability)
                    if avg_rel < 0.5: self.threshold = 0.80 # Tighten requirements
                    else: self.threshold = 0.70
                return None

            if e_type == "EVIDENCE":
                src = event.get("source")
                if not src: return None

                state["received_sources"].add(src)

                # Record evidence
                direction = int(event.get("direction") or 0)
                if "Trend" in src: state["confluence"]["trend"] = direction
                elif "Indicator" in src: state["confluence"]["momentum"] = direction

                # 10615: Harden Bayesian Update against NoneType values
                p_e_h = float(event.get("p_e_h") or 0.50)
                p_e = float(event.get("p_e") or 0.50)
                rel = float(self.brain_reliability.get(src) or 1.0)

                # Weighting
                weighted_p_e_h = 0.50 + (p_e_h - 0.50) * rel
                prior = state["prior"]
                posterior = (weighted_p_e_h * prior) / p_e if p_e > 0 else prior
                state["prior"] = max(0.01, min(0.99, posterior))

                # Update intel for dashboard
                intel_data = {
                    "prob": state["prior"],
                    "regime": state.get("regime", "NORMAL"),
                    "sources": list(state["received_sources"]),
                    "last_source": src,
                    "last_p_e_h": p_e_h,
                    "weighted_p_e_h": weighted_p_e_h,
                    "prior_was": prior
                }
                self.ipc.set_state(f"intel:{symbol}", intel_data)
                self.publish_state(symbol, intel_data)

                state["evidence_trail"].append({
                    "src": src, "dir": direction, "p": state["prior"], "rel": rel
                })

                # Check for Decision
                if all(s in state["received_sources"] for s in self.required_sources):
                    # Mandatory Trend Alignment Check
                    if state["confluence"]["trend"] == 0: return None

                    # Signal direction must match trend
                    action = "BUY" if state["confluence"]["trend"] > 0 else "SELL"

                    # Check Momentum alignment
                    if state["confluence"]["momentum"] != state["confluence"]["trend"]:
                        return None # No alignment

                    if state["prior"] >= self.threshold:
                        # 10620: Acquire Trading Lock (Zero-Tolerance)
                        active_trades = self.ipc.get_state("active_trades", [])
                        if any(t['symbol'] == symbol for t in active_trades):
                            return None # Rule 1.a: No duplicate initial trades

                        if not self.ipc.acquire_trading_lock(symbol):
                            return None

                        res = {
                            "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": action,
                            "probability": state["prior"], "lots": 0.01,
                            "reason": f"MTF_ALIGNED_CONF_{len(state['evidence_trail'])}",
                            "evidence": json.dumps(state["evidence_trail"])
                        }
                        self.symbol_state[symbol] = self._new_state()
                        return res
            return None
        except Exception as e:
            logger.error(f"MetaBrain Process Error for {event.get('symbol')}: {e}")
            return None

    def _new_state(self):
        return {
            "prior": 0.50, "evidence_trail": [], "received_sources": set(),
            "confluence": {"trend": 0, "momentum": 0}
        }

    async def _learning_loop(self):
        """10630: Learn <-> Evaluate <-> Fix Loop."""
        import aiosqlite
        from src.python.execution.ledger import TradeLedger
        ledger = TradeLedger()
        await ledger.init_db()

        while getattr(self, "is_running", True):
            try:
                async with aiosqlite.connect(ledger.db_path) as db:
                    db.row_factory = aiosqlite.Row
                    # Analyze last 50 closed trades
                    async with db.execute("SELECT * FROM trades WHERE status = 'CLOSED' ORDER BY timestamp DESC LIMIT 50") as cursor:
                        recent_trades = [dict(row) for row in await cursor.fetchall()]

                if recent_trades:
                    # Logic: If win rate < 40%, increase Bayesian threshold
                    wins = len([t for t in recent_trades if t.get('profit', 0) > 0])
                    win_rate = wins / len(recent_trades)

                    if win_rate < 0.4:
                        old_t = self.threshold
                        self.threshold = min(0.9, self.threshold + 0.05)
                        msg = f"Fixing: Low win rate {win_rate:.2f}. Increasing threshold {old_t:.2f} -> {self.threshold:.2f}"
                        logger.warning(msg)
                        self.ipc.xadd("stream:learning_events", {"type": "THRESHOLD_ADJ", "msg": msg, "win_rate": win_rate})
                    elif win_rate > 0.6:
                        old_t = self.threshold
                        self.threshold = max(0.6, self.threshold - 0.02)
                        msg = f"Optimizing: Good win rate {win_rate:.2f}. Relaxing threshold {old_t:.2f} -> {self.threshold:.2f}"
                        logger.info(msg)
                        self.ipc.xadd("stream:learning_events", {"type": "THRESHOLD_ADJ", "msg": msg, "win_rate": win_rate})

                    # Update reliability for individual brains
                    for t in recent_trades:
                        trail_str = t.get("evidence")
                        if not trail_str: continue

                        try:
                            trail = json.loads(trail_str)
                            adj = 0.02 if t.get('profit', 0) > 0 else -0.03
                            for e in trail:
                                src = e.get("src")
                                if src:
                                    old_r = float(self.brain_reliability.get(src) or 1.0)
                                    self.brain_reliability[src] = max(0.1, min(1.0, old_r + adj))
                                    if abs(self.brain_reliability[src] - old_r) > 0.01:
                                         self.ipc.xadd("stream:learning_events", {"type": "RELIABILITY_ADJ", "brain": src, "score": self.brain_reliability[src]})
                        except Exception:
                            continue

                self.ipc.set_state("brain_reliability", self.brain_reliability)
                self.ipc.set_state("last_decision", {"msg": "BRAIN: Reliability calibration cycle complete", "time": time.time()})
                self.publish({"type": "RELIABILITY_REPORT", "scores": self.brain_reliability})
                await asyncio.sleep(1800) # Calibration period # Every 30 mins
            except Exception as e:
                logger.error(f"MetaBrain Learning Error: {e}")
                await asyncio.sleep(60)
