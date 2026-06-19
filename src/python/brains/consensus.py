import pandas as pd
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from typing import Dict, Any

class ConsensusEngine:
    def __init__(self):
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        history = data.get("history", [])
        if not history: return {"action": "WAIT", "reason": "No history provided"}
        df = pd.DataFrame(history)

        # HTF Analysis for Alignment
        h4_df = pd.DataFrame(data.get("h4", []))
        htf_struct = self.smc.detect_market_structure(h4_df) if not h4_df.empty else {"trend": "NEUTRAL", "swing_h": 0, "swing_l": 0}

        inds = self.indicators.calculate_all(df)
        atr = inds["atr"]
        structure = self.smc.detect_market_structure(df, atr=atr)
        vsa = self.volatility.analyze_vsa(df)
        trigger = self.smc.detect_candlestick_trigger(df)

        curr_price = df['c'].iloc[-1]

        # Swing Proximity: Reject if buying into resistance or selling into support
        proximity_rejection = False
        if htf_struct["swing_h"] and curr_price >= htf_struct["swing_h"] - (atr * 0.5):
            proximity_rejection = "NEAR_HTF_RESISTANCE"
        if htf_struct["swing_l"] and curr_price <= htf_struct["swing_l"] + (atr * 0.5):
            proximity_rejection = "NEAR_HTF_SUPPORT"

        momentum = "NEUTRAL"
        if inds["rsi"] > 60: momentum = "BULLISH"
        elif inds["rsi"] < 40: momentum = "BEARISH"

        obs = self.smc.detect_order_blocks(df, atr=atr)
        near_ob = False
        active_ob = None
        for ob in obs:
            if ob["type"] == "BULLISH" and curr_price <= ob["top"] + (atr * 0.1):
                near_ob = True
                active_ob = ob
            elif ob["type"] == "BEARISH" and curr_price >= ob["bottom"] - (atr * 0.1):
                near_ob = True
                active_ob = ob

        regime = self.volatility.get_regime(df)

        scores = {
            "trend": 1 if structure["trend"] == "BULLISH" else (-1 if structure["trend"] == "BEARISH" else 0),
            "momentum": 1 if momentum == "BULLISH" else (-1 if momentum == "BEARISH" else 0),
            "structure": 1 if near_ob and structure["trend"] == "BULLISH" else (-1 if near_ob and structure["trend"] == "BEARISH" else 0),
            "volatility": 1 if regime != "HIGH_VOLATILITY" else 0
        }

        # HTF Alignment Bonus
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

        if trigger_confirmed and not proximity_rejection:
            if total_score >= 3: action = "BUY"
            elif total_score <= -3: action = "SELL"

        return {
            "action": action, "score": total_score, "details": scores,
            "vsa": vsa, "atr": atr, "sweep": structure["sweep"], "trigger": trigger,
            "htf_trend": htf_struct["trend"], "proximity_msg": proximity_rejection
        }
