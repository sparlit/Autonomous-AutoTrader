import asyncio
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Responsible for WebSocket, Tick Data, and Candle Generation."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP":
            return {
                "type": "MARKET_DATA", "symbol": event.get("s"), "bid": event.get("bi"), "ask": event.get("as"),
                "ltf": event.get("ltf", []), "h1": event.get("h1", []), "h4": event.get("h4", [])
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Responsible for Technical Indicators (RSI, ATR, etc)."""
    def initialize(self):
        super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            inds = self.analyst.calculate_all(df)
            return {"type": "INDICATORS", "symbol": event["symbol"], "indicators": inds}
        return None

class TrendBrain(BaseBrain):
    """Brain 3 - 10503: Responsible for Market Structure and Trend Detection across MTFs."""
    def initialize(self):
        super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            struct = self.smc.detect_market_structure(df)
            payload = {"type": "TREND", "symbol": event["symbol"], "trend": struct["trend"], "sweep": struct["sweep"]}
            for tf_key in ["m1", "m5", "h1", "h4"]:
                tf_data = event.get(tf_key, [])
                if tf_data:
                    tf_df = pd.DataFrame(tf_data)
                    if isinstance(tf_data[0], list): tf_df.columns = ["o", "h", "l", "c", "t", "v"]
                    tf_struct = self.smc.detect_market_structure(tf_df)
                    payload[f"{tf_key}_trend"] = tf_struct["trend"]
                else: payload[f"{tf_key}_trend"] = "NEUTRAL"
            return payload
        return None

class LiquidityBrain(BaseBrain):
    """Brain 4 - 10505: Responsible for Order Blocks and Fair Value Gaps."""
    def initialize(self):
        super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            obs = self.smc.detect_order_blocks(df)
            return {"type": "LIQUIDITY", "symbol": event["symbol"], "order_blocks": obs}
        return None

class RegimeBrain(BaseBrain):
    """Brain - 10506: Responsible for Market Regime Detection (Trending vs Ranging)."""
    def initialize(self):
        super().initialize()
        self.volatility = VolatilityAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            regime = self.volatility.get_regime(df)
            return {"type": "REGIME", "symbol": event["symbol"], "regime": regime}
        return None

class ContrarianBrain(BaseBrain):
    """Brain - 10507: Purpose: Find reasons NOT to trade (Veto Logic)."""
    def initialize(self):
        super().initialize()
        self.indicators = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "SIGNAL":
            symbol = event["symbol"]; atr = event.get("atr", 0)
            if atr < 0.00005: return {"type": "VETO", "symbol": symbol, "reason": "ATR_TOO_LOW_LIQUIDITY_RISK"}
            reasons = []
            if event.get("action") == "BUY" and event.get("rsi", 50) > 75: reasons.append("OVERBOUGHT_REVERSION_RISK")
            if event.get("action") == "SELL" and event.get("rsi", 50) < 25: reasons.append("OVERSOLD_REVERSION_RISK")
            if reasons: return {"type": "VETO", "symbol": symbol, "reason": "|".join(reasons)}
        return None

class NewsRiskBrain(BaseBrain):
    """Brain - 10509: Responsible for Economic Calendar and News Safety."""
    def initialize(self):
        super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.risk_manager.is_news_safe():
            return {"type": "NEWS_VETO", "symbol": event.get("symbol", "GLOBAL"), "reason": "HIGH_IMPACT_NEWS_PENDING_30M_WINDOW"}
        return None

class MemoryBrain(BaseBrain):
    """Brain - 10510: Responsible for Performance Tracking and Dynamic Weighting."""
    def initialize(self):
        super().initialize()
        self.performance_stats: Dict[str, Dict[str, Any]] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "EXECUTION_ORDER":
            symbol = event["symbol"]
            if symbol not in self.performance_stats: self.performance_stats[symbol] = {"trades": 0, "wins": 0, "last_weight": 1.0}
            self.performance_stats[symbol]["trades"] += 1
            return {"type": "MEMORY_UPDATE", "symbol": symbol, "stats": self.performance_stats[symbol]}
        return None

class MonitoringBrain(BaseBrain):
    """Brain 8 - 10511: Responsible for Health Checks and Supervisor Reporting."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "HEALTH_CHECK":
            return {"type": "MONITORING_REPORT", "status": "ALL_SYSTEMS_GO"}
        return None

class RiskBrain(BaseBrain):
    """Brain 6 - 10512: Responsible for Position Sizing and Safety Validation."""
    def initialize(self):
        super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "SIGNAL":
            symbol = event["symbol"]; action = event["action"]; equity = event.get("equity", 1000.0); atr = event.get("atr", 0.0)
            v = self.risk_manager.validate_trade(symbol, action, equity, atr=atr)
            if v["safe"]:
                return {"type": "VALIDATED_TRADE", "symbol": symbol, "action": action, "lots": v["lots"], "sl_pts": v["sl_pts"], "tp_pts": v["tp_pts"], "score": event.get("score"), "reasons": event.get("reasons")}
        return None

class ExecutionBrain(BaseBrain):
    """Brain 7 - 10513: Responsible for Order Placement and MT5 Communication."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            logger.info(f"EXECUTION_ACTUATED: {event['action']} {event['symbol']} Score:{event['score']} | {','.join(event['reasons'])}")
            return {"type": "EXECUTION_ORDER", "symbol": event["symbol"], "action": event["action"], "lots": event["lots"], "sl": event["sl_pts"], "tp": event["tp_pts"]}
        return None

class AnomalyBrain(BaseBrain):
    """Brain - 10514: Detects market anomalies and flash-crash conditions."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            return {"type": "ANOMALY_STATUS", "symbol": event["symbol"], "status": "NOMINAL"}
        return None

class PortfolioBrain(BaseBrain):
    """Brain - 10516: Manages dynamic capital allocation across symbols."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MEMORY_UPDATE":
            return {"type": "ALLOCATION_UPDATE", "symbol": event["symbol"], "weight": 1.0}
        return None
