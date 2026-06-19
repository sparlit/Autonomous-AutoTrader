from src.python.brains.base import BaseBrain
from src.python.brains.consensus import ConsensusEngine
from typing import Dict, Any
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
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"htf_trend": "BULLISH", "alignment": True}

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
