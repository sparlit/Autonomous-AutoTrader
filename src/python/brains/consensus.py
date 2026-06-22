import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from src.python.brains.base import BaseBrain
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Bayesian Probability Engine.
    Self-Learning: Adjusts evidence weights based on brain reliability reports.
    Explainability: Returns detailed impact of each brain on final posterior.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.70, ipc: Any = None):
        super().__init__(name, cpu_affinity, ipc=ipc)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.brain_reliability: Dict[str, float] = {}
        self.required_sources = ["Trend_1", "Indicator_1", "Liquidity_1", "Regime_1"]

    async def initialize(self):
        await super().initialize()
        # Additional async initialization if needed

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None
        if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
        state = self.symbol_state[symbol]; e_type = event.get("type")
        if e_type == "MARKET_DATA_REFRESH": self.symbol_state[symbol] = self._new_state(); return None
        if e_type == "RELIABILITY_REPORT": self.brain_reliability = event.get("scores", {}); return None
        if e_type == "REGIME_STATUS": state["regime"] = event["regime"]; state["received_sources"].add(event["source"])
        elif e_type in ["VETO", "NEWS_VETO"]: state["veto"] = True; state["veto_reason"] = event.get("reason")
        elif e_type == "EVIDENCE":
            p_e_h = event.get("p_e_h", 0.50); p_e = event.get("p_e", 0.50)
            rel = self.brain_reliability.get(event["source"], 1.0)
            # 12601: Reliability-weighted evidence
            weighted_p_e_h = 0.50 + (p_e_h - 0.50) * rel
            prior = state["prior"]; posterior = (weighted_p_e_h * prior) / p_e
            impact = posterior - prior
            state["prior"] = max(0.01, min(0.99, posterior))
            # 12602: Rich explainability trail
            state["evidence_trail"].append({"source": event["source"], "direction": event.get("direction", 0), "posterior": state["prior"], "impact": impact, "reliability": rel})
            state["received_sources"].add(event["source"])
            if "data" in event:
                state["atr"] = event["data"].get("atr", state["atr"]); state["rsi"] = event["data"].get("rsi", state["rsi"])
        if all(src in state["received_sources"] for src in self.required_sources):
            if state["prior"] >= self.threshold and not state["veto"]:
                action = self._determine_direction(state)
                if action != "WAIT":
                    res = {
                        "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": action,
                        "probability": state["prior"], "regime": state["regime"], "atr": state["atr"], "rsi": state["rsi"],
                        "evidence_trail": state["evidence_trail"],
                        # 12603: Detailed explainability summary
                        "explainability": [f"{e['source']} ({e['reliability']:.2f}): {'+' if e['impact'] >= 0 else ''}{e['impact']:.2f} -> P={e['posterior']:.2f}" for e in state['evidence_trail']]
                    }
                    state["received_sources"] = set(); return res
        return None

    def _new_state(self):
        return {"prior": 0.50, "evidence_trail": [], "regime": "NORMAL", "veto": False, "received_sources": set(), "atr": 0.0, "rsi": 50}

    def _determine_direction(self, state):
        directions = [e["direction"] for e in state["evidence_trail"] if e["direction"] != 0]
        if not directions: return "WAIT"
        net_dir = sum(directions); return "BUY" if net_dir > 0 else ("SELL" if net_dir < 0 else "WAIT")

class ConsensusEngine:
    """30001: Legacy Consensus Engine for synchronous worker processing."""
    def __init__(self):
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()
        self._thread_pool = ThreadPoolExecutor(max_workers=8)
        self.magic = 30001

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hist_data = data.get("history", [])
        if hist_data and isinstance(hist_data[0], list): hist_data = self._parse_history(hist_data)
        if not hist_data: return {"act": "WAIT", "reason": "EMPTY_HIST", "m_id": 30003}

        df = pd.DataFrame(hist_data)
        inds = self.indicators.calculate_all(df)
        atr = inds.get("atr", 0.0)
        vsa = self.volatility.analyze_vsa(df)
        trigger = self.smc.detect_candlestick_trigger(df)

        from src.python.brains.strategies.swing_master import SwingMaster
        from src.python.brains.strategies.day_master import DayMaster
        from src.python.brains.strategies.carry_master import CarryMaster
        from src.python.brains.strategies.scalp_master import ScalpMaster

        strats = [SwingMaster("S"), DayMaster("D"), CarryMaster("C"), ScalpMaster("SC")]
        strat_results = [asyncio.run(s.process(data)) for s in strats]

        votes = [r for r in strat_results if r and r.direction != 0]
        net_direction = sum(v.direction for v in votes)
        regime = self.volatility.get_regime(df)

        action = "WAIT"
        if net_direction >= 2: action = "BUY"
        elif net_direction <= -2: action = "SELL"

        return {
            "act": action,
            "scr": net_direction,
            "atr": atr,
            "vsa": vsa,
            "regime": regime,
            "m_id": 30003,
            "magic": self.magic
        }
