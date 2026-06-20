import pandas as pd
import numpy as np
import sys
import os
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# Tier 1: Rust Integration
try:
    # Attempt to import the high-speed Rust validator
    sys.path.append(os.path.join(os.path.dirname(__file__), '../bridge'))
    import aat_rust
    RUST_ENABLED = True
except ImportError:
    RUST_ENABLED = False

class ConsensusEngine:
    def __init__(self):
        """Magic: 3001"""
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self.magic = 3001

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        """Magic: 3002"""
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 3003"""
        hist_data = data.get("history", [])
        if hist_data and isinstance(hist_data[0], list): hist_data = self._parse_history(hist_data)
        if not hist_data: return {"act": "WAIT", "reason": "No history", "m_id": 3003}
        df = pd.DataFrame(hist_data)

        h4_raw = data.get("h4", [])
        if h4_raw and isinstance(h4_raw[0], list): h4_raw = self._parse_history(h4_raw)
        h4_df = pd.DataFrame(h4_raw)

        f_htf = self._thread_pool.submit(self.smc.detect_market_structure, h4_df) if not h4_df.empty else None
        f_inds = self._thread_pool.submit(self.indicators.calculate_all, df)
        f_vsa = self._thread_pool.submit(self.volatility.analyze_vsa, df)
        f_trig = self._thread_pool.submit(self.smc.detect_candlestick_trigger, df)

        inds = f_inds.result()
        atr = inds.get("atr", 0.0)
        structure = self.smc.detect_market_structure(df, atr=atr)
        htf_struct = f_htf.result() if f_htf else {"trend": "NEUTRAL", "swing_h": 0, "swing_l": 0}
        vsa = f_vsa.result()
        trigger = f_trig.result()

        curr_price = df['c'].iloc[-1]

        proximity_rejection = False
        if htf_struct.get("swing_h") and curr_price >= htf_struct["swing_h"] - (atr * 0.5):
            proximity_rejection = "NEAR_HTF_RES"
        if htf_struct.get("swing_l") and curr_price <= htf_struct["swing_l"] + (atr * 0.5):
            proximity_rejection = "NEAR_HTF_SUP"

        momentum = "NEUTRAL"
        if inds.get("rsi", 50) > 60: momentum = "BULLISH"
        elif inds.get("rsi", 50) < 40: momentum = "BEARISH"

        obs = self.smc.detect_order_blocks(df, atr=atr)
        near_ob = False; active_ob = None
        for ob in obs:
            if ob["type"] == "BULLISH" and curr_price <= ob["top"] + (atr * 0.1):
                near_ob = True; active_ob = ob
            elif ob["type"] == "BEARISH" and curr_price >= ob["bottom"] - (atr * 0.1):
                near_ob = True; active_ob = ob

        regime = self.volatility.get_regime(df)

        scores = {
            "trend": 1 if structure["trend"] == "BULLISH" else (-1 if structure["trend"] == "BEARISH" else 0),
            "momentum": 1 if momentum == "BULLISH" else (-1 if momentum == "BEARISH" else 0),
            "structure": 1 if near_ob and structure["trend"] == "BULLISH" else (-1 if near_ob and structure["trend"] == "BEARISH" else 0),
            "volatility": 1 if regime != "HIGH_VOLATILITY" else 0
        }

        if htf_struct["trend"] == "BULLISH" and structure["trend"] == "BULLISH": scores["trend"] += 1
        if htf_struct["trend"] == "BEARISH" and structure["trend"] == "BEARISH": scores["trend"] -= 1

        if vsa["effort"] == "HIGH" and vsa["result"] == "STRONG":
            if structure["trend"] == "BULLISH": scores["momentum"] += 1
            elif structure["trend"] == "BEARISH": scores["momentum"] -= 1

        if structure["sweep"] == "BULLISH_SWEEP": scores["structure"] += 2
        elif structure["sweep"] == "BEARISH_SWEEP": scores["structure"] -= 2

        trigger_confirmed = False
        if trigger:
            if "BULLISH" in trigger and (scores["trend"] + scores["structure"]) > 0: trigger_confirmed = True
            if "BEARISH" in trigger and (scores["trend"] + scores["structure"]) < 0: trigger_confirmed = True

        total_score = sum(scores.values())
        action = "WAIT"

        # Zero-Tolerance Threshold
        if trigger_confirmed and not proximity_rejection:
            if total_score >= 4: action = "BUY"
            elif total_score <= -4: action = "SELL"

        # Tier 1: Final Fast-Veto via Rust
        if action != "WAIT" and RUST_ENABLED:
            dir_int = 1 if action == "BUY" else -1
            # Confidence based on score normalized
            conf = min(1.0, abs(total_score) / 6.0)
            if not aat_rust.validate_signal_fast(dir_int, conf):
                action = "WAIT"
                proximity_rejection = "RUST_VETO"

        draw_commands = []
        if active_ob:
            draw_commands.append({
                "type": "RECTANGLE", "name": f"OB_{active_ob['type']}_{active_ob['index']}",
                "top": active_ob["top"], "bottom": active_ob["bottom"],
                "color": "0,255,0" if active_ob["type"] == "BULLISH" else "255,0,0"
            })

        return {
            "act": action, "scr": total_score, "htf": htf_struct["trend"],
            "vsa": vsa, "atr": atr, "sweep": structure["sweep"], "trigger": trigger,
            "prox": proximity_rejection, "draw": draw_commands,
            "m_id": 3003, "magic": self.magic, "rust": RUST_ENABLED
        }
