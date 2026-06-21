import pandas as pd
import numpy as np
import sys
import os
import polars as pl
import asyncio
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from src.python.brains.ml_trainer import MLTrainer
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# Tier 1: Rust Integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../bridge'))
try:
    import aat_institutional_core as aat_heavy
    RUST_HEAVY_ENABLED = True
    # Initializing global instance for the process
    _heavy = aat_heavy.HeavyEngine()
except ImportError:
    RUST_HEAVY_ENABLED = False

class ConsensusEngine:
    def __init__(self):
        """Magic: 30001"""
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()
        self.ml = MLTrainer()
        self._thread_pool = ThreadPoolExecutor(max_workers=8)
        self.magic = 30001

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        """Magic: 30002"""
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 30003"""
        hist_data = data.get("history", [])
        if hist_data and isinstance(hist_data[0], list): hist_data = self._parse_history(hist_data)
        if not hist_data: return {"act": "WAIT", "reason": "EMPTY_HIST", "m_id": 30003}

        df = pd.DataFrame(hist_data)

        # Parallel Execution of Sub-Analyst Tasks
        f_inds = self._thread_pool.submit(self.indicators.calculate_all, df)
        f_vsa = self._thread_pool.submit(self.volatility.analyze_vsa, df)
        f_trig = self._thread_pool.submit(self.smc.detect_candlestick_trigger, df)

        inds = f_inds.result()
        atr = inds.get("atr", 0.0)
        vsa = f_vsa.result()
        trigger = f_trig.result()

        # Strategy Suite Processing
        from src.python.brains.strategies.swing_master import SwingMaster
        from src.python.brains.strategies.day_master import DayMaster
        from src.python.brains.strategies.carry_master import CarryMaster
        from src.python.brains.strategies.scalp_master import ScalpMaster

        # In a process-pool worker, we execute these synchronously within the thread pool
        # to achieve the hybrid multithread/parallel requirement.
        strats = [SwingMaster("S"), DayMaster("D"), CarryMaster("C"), ScalpMaster("SC")]

        # We wrap the async process calls for the synchronous context of this worker task
        def run_strat(s, d):
            return asyncio.run(s.process(d))

        strat_results = [self._thread_pool.submit(run_strat, s, data).result() for s in strats]

        # Aggregate Strategy Votes
        votes = [r for r in strat_results if r and r.direction != 0]
        net_direction = sum(v.direction for v in votes)

        # ML Regime Filtering
        regime = self.volatility.get_regime(df)

        action = "WAIT"
        if net_direction >= 2: action = "BUY"
        elif net_direction <= -2: action = "SELL"

        # Rust-Powered Pre-Trade Risk Check
        if RUST_HEAVY_ENABLED and action != "WAIT":
             if not _heavy.check_risk_decimal(10000.0, 1.0, atr * 2.0):
                 action = "WAIT"

        return {
            "act": action,
            "scr": net_direction,
            "atr": atr,
            "vsa": vsa,
            "regime": regime,
            "m_id": 30003,
            "magic": self.magic,
            "rust": RUST_HEAVY_ENABLED
        }
