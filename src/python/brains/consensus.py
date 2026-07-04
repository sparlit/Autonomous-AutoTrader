import asyncio
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """V4.0-PRO: Bayesian Probability Engine with Institutional Assessments."""
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, ipc: Any = None):
        super().__init__(name, cpu_affinity, ipc=ipc)
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.reliability = {}

    async def initialize(self):
        await super().initialize()
        self.reliability = self.ipc.get_state("brain_reliability", {})
        asyncio.create_task(self._reliability_sync_loop())

    async def _reliability_sync_loop(self):
        while self.is_running:
            try:
                new_rel = self.ipc.get_state("brain_reliability", {})
                if new_rel: self.reliability = new_rel
            except: pass
            await asyncio.sleep(60)

    def _new_state(self):
        return {"prior": 0.5, "evidence": [], "ts": time.time()}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None

        if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
        state = self.symbol_state[symbol]

        if event.get("type") == "EVIDENCE":
            src = event.get("source", "Unknown")
            p_e_h = float(event.get("p_e_h") or 0.5)
            rel = float(self.reliability.get(src, 0.70))

            # V4.0 Weighted Bayesian Update
            weighted_p_e_h = 0.5 + (p_e_h - 0.5) * rel
            prior = state["prior"]
            posterior = (weighted_p_e_h * prior) / 0.5
            state["prior"] = max(0.01, min(0.99, posterior))
            state["ts"] = time.time()

            # Update Intel for Dashboard
            intel_data = {
                "prob": state["prior"],
                "last_src": src,
                "regime": self.ipc.get_state(f"intel:{symbol}", {}).get("regime", "NORMAL"),
                "ts": time.time()
            }
            self.ipc.set_state(f"intel:{symbol}", intel_data)

            if state["prior"] > 0.80:
                return {
                    "type": "PROBABILISTIC_SIGNAL",
                    "symbol": symbol,
                    "action": "BUY" if p_e_h > 0.5 else "SELL",
                    "probability": state["prior"],
                    "reason": f"BAYESIAN_CONFLUENCE_VIA_{src}"
                }

        elif event.get("type") == "REGIME_STATUS":
            intel = self.ipc.get_state(f"intel:{symbol}", {"prob": 0.5})
            intel["regime"] = event.get("regime", "NORMAL")
            self.ipc.set_state(f"intel:{symbol}", intel)

        self.publish_state(symbol, {"prob": state["prior"]})
        return None
