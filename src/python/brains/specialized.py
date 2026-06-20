from src.python.brains.base import BaseBrain, SignalPayload
from src.python.brains.consensus import ConsensusEngine
from src.python.analyst.price_action import SMCAnalyst
from typing import Dict, Any, List, Optional
import pandas as pd
import asyncio
import time

class DecisionBrain(BaseBrain):
    def __init__(self, name: str):
        """Magic: 1001"""
        super().__init__(name)
        self.engine = ConsensusEngine()
        self.magic = 1001

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.engine.analyze_sync(data)

class HTFAnalysisBrain(BaseBrain):
    def __init__(self, name: str):
        """Magic: 1002"""
        super().__init__(name)
        self.smc = SMCAnalyst()
        self.magic = 1002

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("t") != "DP": return {"m_id": 1002}
        h1_raw = data.get("h1", [])
        h4_raw = data.get("h4", [])

        h1_df = pd.DataFrame(h1_raw, columns=['o','h','l','c','t','v']) if h1_raw else pd.DataFrame()
        h4_df = pd.DataFrame(h4_raw, columns=['o','h','l','c','t','v']) if h4_raw else pd.DataFrame()

        h1_struct = self.smc.detect_market_structure(h1_df) if not h1_df.empty else {"trend": "NEUTRAL"}
        h4_struct = self.smc.detect_market_structure(h4_df) if not h4_df.empty else {"trend": "NEUTRAL"}

        alignment = (h1_struct["trend"] == h4_struct["trend"]) and h1_struct["trend"] != "NEUTRAL"
        return {
            "h1_trend": h1_struct["trend"],
            "h4_trend": h4_struct["trend"],
            "alignment": alignment,
            "m_id": 1002
        }

class LTFTriggerBrain(BaseBrain):
    def __init__(self, name: str):
        """Magic: 1003"""
        super().__init__(name)
        self.smc = SMCAnalyst()
        self.magic = 1003

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ltf_raw = data.get("ltf", [])
        if not ltf_raw: return {"m_id": 1003}
        df = pd.DataFrame(ltf_raw, columns=['o','h','l','c','t','v'])
        trigger = self.smc.detect_candlestick_trigger(df)
        return {
            "trigger": trigger,
            "m_id": 1003
        }

class CorrelationBrain(BaseBrain):
    def __init__(self, name: str):
        """Magic: 1004"""
        super().__init__(name)
        self.magic = 1004
        self.currency_map = {
            "EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"),
            "USDJPY": ("USD", "JPY"), "AUDUSD": ("AUD", "USD"),
            "USDCAD": ("USD", "CAD"), "USDCHF": ("USD", "CHF"),
            "NZDUSD": ("NZD", "USD")
        }

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"correlation_safe": True, "m_id": 1004}

    def check_exposure(self, symbol: str, action: str, active_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Magic: 1006"""
        base, quote = self.currency_map.get(symbol, (symbol[:3], symbol[3:]))
        exposure = {}
        for trade in active_trades:
            t_sym = trade.get("symbol", "UNKNOWN")
            t_base, t_quote = self.currency_map.get(t_sym, (t_sym[:3], t_sym[3:]))
            dir_mult = 1 if trade.get("action") == "BUY" else -1
            lots = trade.get("lots", 0.01)
            exposure[t_base] = exposure.get(t_base, 0) + (dir_mult * lots)
            exposure[t_quote] = exposure.get(t_quote, 0) - (dir_mult * lots)

        dir_mult = 1 if action == "BUY" else -1
        new_base_exp = exposure.get(base, 0) + dir_mult * 0.01
        new_quote_exp = exposure.get(quote, 0) - dir_mult * 0.01

        if abs(new_base_exp) > 0.5 or abs(new_quote_exp) > 0.5:
            return {"safe": False, "reason": "EXP_LIMIT", "m_id": 1006}
        return {"safe": True, "m_id": 1006}

class ContextBrain(BaseBrain):
    def __init__(self, name: str):
        """Magic: 1005"""
        super().__init__(name)
        self.magic = 1005
        self.global_context = {"news_high_impact": False, "index_trend": "NEUTRAL", "last_updated": 0, "m_id": 1005}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.global_context

    async def update_global_context(self):
        """Magic: 1007"""
        while True:
            self.global_context["last_updated"] = time.time()
            await asyncio.sleep(60)
