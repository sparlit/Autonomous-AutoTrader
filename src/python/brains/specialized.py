from src.python.brains.base import BaseBrain
from src.python.brains.consensus import ConsensusEngine
<<<<<<< HEAD
from src.python.analyst.price_action import SMCAnalyst
from typing import Dict, Any, List
import pandas as pd
import asyncio
import time
=======
from typing import Dict, Any
import asyncio
>>>>>>> origin/main

class DecisionBrain(BaseBrain):
    def __init__(self, name: str):
        super().__init__(name)
        self.engine = ConsensusEngine()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
<<<<<<< HEAD
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
        return {}

class CorrelationBrain(BaseBrain):
    def __init__(self, name: str):
        super().__init__(name)
        self.currency_map = {
            "EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"),
            "USDJPY": ("USD", "JPY"), "AUDUSD": ("AUD", "USD"),
            "USDCAD": ("USD", "CAD"), "USDCHF": ("USD", "CHF"),
            "NZDUSD": ("NZD", "USD")
        }

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"correlation_safe": True}

    def check_exposure(self, symbol: str, action: str, active_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        base, quote = self.currency_map.get(symbol, (symbol[:3], symbol[3:]))
        exposure = {}
        for trade in active_trades:
            t_base, t_quote = self.currency_map.get(trade["symbol"], (trade["symbol"][:3], trade["symbol"][3:]))
            dir_mult = 1 if trade["action"] == "BUY" else -1
            exposure[t_base] = exposure.get(t_base, 0) + dir_mult
            exposure[t_quote] = exposure.get(t_quote, 0) - dir_mult
        dir_mult = 1 if action == "BUY" else -1
        new_base_exp = exposure.get(base, 0) + dir_mult
        new_quote_exp = exposure.get(quote, 0) - dir_mult
        if abs(new_base_exp) > 2 or abs(new_quote_exp) > 2:
            return {"safe": False, "reason": f"Max exposure exceeded for {base if abs(new_base_exp)>2 else quote}"}
        return {"safe": True}

class ContextBrain(BaseBrain):
    """Parallel engine for Global Market Context (News, Sentiment, Correlated Indices)."""
    def __init__(self, name: str):
        super().__init__(name)
        self.global_context = {
            "news_high_impact": False,
            "index_trend": "NEUTRAL",
            "last_updated": 0
        }

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # This brain doesn't process symbol ticks directly, it updates global state
        return self.global_context

    async def update_global_context(self):
        """Continuously update global variables in a parallel async loop."""
        while True:
            # Parallel fetching logic would go here
            # For now, we mock the update
            self.global_context["last_updated"] = time.time()
            await asyncio.sleep(60) # Update every minute
=======
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
>>>>>>> origin/main
