from src.python.brains.base import BaseBrain
from src.python.brains.consensus import ConsensusEngine
from src.python.analyst.price_action import SMCAnalyst
from typing import Dict, Any
import pandas as pd
import asyncio

class DecisionBrain(BaseBrain):
    def __init__(self, name: str):
        super().__init__(name)
        self.engine = ConsensusEngine()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("type") == "DATA_PUSH":
            return await self.engine.analyze(data)
        return {"action": "WAIT"}

class HTFAnalysisBrain(BaseBrain):
    def __init__(self, name: str):
        super().__init__(name)
        self.smc = SMCAnalyst()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("type") != "DATA_PUSH": return {}

        h1_df = pd.DataFrame(data.get("h1", []))
        h4_df = pd.DataFrame(data.get("h4", []))

        h1_struct = self.smc.detect_market_structure(h1_df) if not h1_df.empty else {"trend": "NEUTRAL"}
        h4_struct = self.smc.detect_market_structure(h4_df) if not h4_df.empty else {"trend": "NEUTRAL"}

        return {
            "h1_trend": h1_struct["trend"],
            "h4_trend": h4_struct["trend"],
            "alignment": h1_struct["trend"] == h4_struct["trend"] and h1_struct["trend"] != "NEUTRAL"
        }

class LTFTriggerBrain(BaseBrain):
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        history = data.get("history", [])
        if len(history) < 2: return {"trigger": False}
        last = history[-1]
        prev = history[-2]
        engulfing_buy = last['c'] > prev['h'] and last['c'] > last['o']
        engulfing_sell = last['c'] < prev['l'] and last['c'] < last['o']
        return {"buy_trigger": engulfing_buy, "sell_trigger": engulfing_sell}

class CorrelationBrain(BaseBrain):
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"correlation_safe": True}
