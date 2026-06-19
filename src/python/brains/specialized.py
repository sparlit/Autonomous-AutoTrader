from src.python.brains.base import BaseBrain
from src.python.brains.consensus import ConsensusEngine
from src.python.analyst.price_action import SMCAnalyst
from typing import Dict, Any, List
import pandas as pd
import asyncio
import time

class DecisionBrain(BaseBrain):
    def __init__(self, name: str):
        """
        Initialize a DecisionBrain with a consensus engine for decision coordination.
        
        Parameters:
            name (str): The name identifier for this brain.
        """
        super().__init__(name)
        self.engine = ConsensusEngine()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a wait action.
        
        Returns:
        	Dict[str, Any]: Dictionary containing {"action": "WAIT"}.
        """
        return {"action": "WAIT"}

class HTFAnalysisBrain(BaseBrain):
    def __init__(self, name: str):
        """
        Initialize an HTF analysis brain for market structure detection.
        
        Parameters:
        	name (str): Name identifier for this brain instance
        """
        super().__init__(name)
        self.smc = SMCAnalyst()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market structure across H1 and H4 timeframes to detect trend alignment.
        
        Parameters:
            data (Dict[str, Any]): Market data containing "type", "h1", and "h4" keys.
                Only processes data with type "DATA_PUSH".
        
        Returns:
            Dict[str, Any]: If type is "DATA_PUSH", contains "h1_trend", "h4_trend", and "alignment"
                (true if both trends match and neither is neutral). Empty dict otherwise.
        """
        if data.get("type") != "DATA_PUSH": return {}
        h1_df = pd.DataFrame(data.get("h1", []))
        h4_df = pd.DataFrame(data.get("h4", []))
        h1_struct = self.smc.detect_market_structure(h1_df) if not h1_df.empty else {"trend": "NEUTRAL"}
        h4_struct = self.smc.detect_market_structure(h4_df) if not h4_df.empty else {"trend": "NEUTRAL"}
        return {"h1_trend": h1_struct["trend"], "h4_trend": h4_struct["trend"], "alignment": h1_struct["trend"] == h4_struct["trend"] and h1_struct["trend"] != "NEUTRAL"}

class LTFTriggerBrain(BaseBrain):
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for lower timeframe trigger detection.
        
        Returns:
            dict: An empty dictionary.
        """
        return {}

class CorrelationBrain(BaseBrain):
    def __init__(self, name: str):
        """
        Initialize a CorrelationBrain instance with a currency pair mapping.
        
        The currency_map dictionary maps FX symbols to their base and quote currency pairs.
        
        Parameters:
        	name (str): The name identifier for this brain instance.
        """
        super().__init__(name)
        self.currency_map = {"EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"), "USDJPY": ("USD", "JPY"), "AUDUSD": ("AUD", "USD"), "USDCAD": ("USD", "CAD"), "USDCHF": ("USD", "CHF"), "NZDUSD": ("NZD", "USD")}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Indicate that the current correlation is safe.
        
        Returns:
        	A dictionary with "correlation_safe" set to True.
        """
        return {"correlation_safe": True}

    def check_exposure(self, symbol: str, action: str, active_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if a proposed trade would exceed maximum currency exposure limits.
        
        Computes current currency exposure from active trades, then determines if adding
        the proposed trade would cause any currency's absolute exposure to exceed 2.
        
        Parameters:
            symbol (str): Currency pair symbol for the proposed trade.
            action (str): Trade action ("BUY" or "SELL").
            active_trades (List[Dict[str, Any]]): List of existing trades, each containing "symbol" and "action" keys.
        
        Returns:
            Dict[str, Any]: A dict with "safe" (bool) indicating whether the trade is safe. 
            If not safe, includes "reason" (str) naming the currency that exceeded the limit.
        """
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
        if abs(new_base_exp) > 2 or abs(new_quote_exp) > 2: return {"safe": False, "reason": f"Max exposure exceeded for {base if abs(new_base_exp)>2 else quote}"}
        return {"safe": True}

class ContextBrain(BaseBrain):
    def __init__(self, name: str):
        """
        Initialize a ContextBrain instance with a neutral global context state.
        """
        super().__init__(name)
        self.global_context = {"news_high_impact": False, "index_trend": "NEUTRAL", "last_updated": 0}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve the current global context state.
        
        Returns:
            The global context dictionary containing news impact status, index trend, and last update time.
        """
        return self.global_context

    async def update_global_context(self):
        """
        Update the global context's last-updated timestamp every 60 seconds indefinitely.
        """
        while True:
            self.global_context["last_updated"] = time.time()
            await asyncio.sleep(60)
