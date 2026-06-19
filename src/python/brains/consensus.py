import asyncio
from typing import Dict, Any, List
import pandas as pd
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst

class ConsensusEngine:
    def __init__(self):
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        history = data.get("history", [])
        if not history:
            return {"action": "WAIT", "reason": "No history provided"}

        df = pd.DataFrame(history)

        structure = self.smc.detect_market_structure(df)
        inds = self.indicators.calculate_all(df)

        momentum = "NEUTRAL"
        if inds["rsi"] > 60: momentum = "BULLISH"
        elif inds["rsi"] < 40: momentum = "BEARISH"

        obs = self.smc.detect_order_blocks(df)
        curr_price = df['c'].iloc[-1]
        near_ob = False
        active_ob = None
        for ob in obs:
            if ob["type"] == "BULLISH" and curr_price <= ob["top"] * 1.001:
                near_ob = True
                active_ob = ob
            elif ob["type"] == "BEARISH" and curr_price >= ob["bottom"] * 0.999:
                near_ob = True
                active_ob = ob

        regime = self.volatility.get_regime(df)

        scores = {
            "trend": 1 if structure["trend"] == "BULLISH" else (-1 if structure["trend"] == "BEARISH" else 0),
            "momentum": 1 if momentum == "BULLISH" else (-1 if momentum == "BEARISH" else 0),
            "structure": 1 if near_ob and structure["trend"] == "BULLISH" else (-1 if near_ob and structure["trend"] == "BEARISH" else 0),
            "volatility": 1 if regime != "HIGH_VOLATILITY" else 0
        }

        total_score = sum(scores.values())

        action = "WAIT"
        if total_score >= 3:
            action = "BUY"
        elif total_score <= -3:
            action = "SELL"

        # Draw commands for MT5
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
            "draw": draw_commands
        }
