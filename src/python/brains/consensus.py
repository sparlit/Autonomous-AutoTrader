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
        """Synchronous analysis for multi-processing."""
        history = data.get("history", [])
        if not history: return {"action": "WAIT", "reason": "No history provided"}
        df = pd.DataFrame(history)

        inds = self.indicators.calculate_all(df)
        atr = inds["atr"]
        structure = self.smc.detect_market_structure(df, atr=atr)
        vsa = self.volatility.analyze_vsa(df)

        momentum = "NEUTRAL"
        if inds["rsi"] > 60: momentum = "BULLISH"
        elif inds["rsi"] < 40: momentum = "BEARISH"

        obs = self.smc.detect_order_blocks(df, atr=atr)
        curr_price = df['c'].iloc[-1]
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

        if vsa["effort"] == "HIGH" and vsa["result"] == "STRONG":
            if structure["trend"] == "BULLISH": scores["momentum"] += 1
            elif structure["trend"] == "BEARISH": scores["momentum"] -= 1
        elif vsa["anomaly"] == "ABSORPTION":
            scores["momentum"] = 0

        if structure["sweep"] == "BULLISH_SWEEP": scores["structure"] += 2
        elif structure["sweep"] == "BEARISH_SWEEP": scores["structure"] -= 2

        total_score = sum(scores.values())
        action = "WAIT"
        if total_score >= 3: action = "BUY"
        elif total_score <= -3: action = "SELL"

        draw_commands = []
        if active_ob:
            draw_commands.append({
                "type": "RECTANGLE",
                "name": f"OB_{active_ob['type']}_{active_ob['index']}",
                "top": active_ob["top"],
                "bottom": active_ob["bottom"],
                "color": "0,255,0" if active_ob["type"] == "BULLISH" else "255,0,0"
            })

        return {
            "action": action,
            "score": total_score,
            "details": scores,
            "vsa": vsa,
            "draw": draw_commands,
            "atr": atr,
            "sweep": structure["sweep"]
        }
