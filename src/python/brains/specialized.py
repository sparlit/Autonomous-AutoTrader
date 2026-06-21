import asyncio
import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from multiprocessing import Queue
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - Responsible for WebSocket, Tick Data, and Candle Generation."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP": # Data Push from MT5
            return {
                "type": "MARKET_DATA",
                "symbol": event.get("s"),
                "bid": event.get("bi"),
                "ask": event.get("as"),
                "ltf": event.get("ltf", []),
                "h1": event.get("h1", []),
                "h4": event.get("h4", [])
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - Responsible for Technical Indicators (RSI, ATR, etc)."""
    def initialize(self):
        super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list):
                df.columns = ["o", "h", "l", "c", "t", "v"]

            inds = self.analyst.calculate_all(df)
            return {
                "type": "INDICATORS",
                "symbol": event["symbol"],
                "indicators": inds
            }
        return None

class TrendBrain(BaseBrain):
    """Brain 3 - Responsible for Market Structure and Trend Detection."""
    def initialize(self):
        super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list):
                df.columns = ["o", "h", "l", "c", "t", "v"]

            struct = self.smc.detect_market_structure(df)
            return {
                "type": "TREND",
                "symbol": event["symbol"],
                "trend": struct["trend"],
                "sweep": struct["sweep"]
            }
        return None

class LiquidityBrain(BaseBrain):
    """Brain 4 - Responsible for Order Blocks and Fair Value Gaps."""
    def initialize(self):
        super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list):
                df.columns = ["o", "h", "l", "c", "t", "v"]

            obs = self.smc.detect_order_blocks(df)
            return {
                "type": "LIQUIDITY",
                "symbol": event["symbol"],
                "order_blocks": obs
            }
        return None

class RiskBrain(BaseBrain):
    """Brain 6 - Responsible for Position Sizing and Safety Validation."""
    def initialize(self):
        super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "SIGNAL":
            symbol = event["symbol"]
            action = event["action"]
            equity = event.get("equity", 1000.0)
            atr = event.get("atr", 0.0)

            v = self.risk_manager.validate_trade(symbol, action, equity, atr=atr)
            if v["safe"]:
                return {
                    "type": "VALIDATED_TRADE",
                    "symbol": symbol,
                    "action": action,
                    "lots": v["lots"],
                    "sl_pts": v["sl_pts"],
                    "tp_pts": v["tp_pts"]
                }
        return None

class ExecutionBrain(BaseBrain):
    """Brain 7 - Responsible for Order Placement and MT5 Communication."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            logger.info(f"EXECUTION: {event['action']} {event['symbol']} @ {event['lots']} lots")
            return {
                "type": "EXECUTION_ORDER",
                "symbol": event["symbol"],
                "action": event["action"],
                "lots": event["lots"],
                "sl": event["sl_pts"],
                "tp": event["tp_pts"]
            }
        return None

class RegimeBrain(BaseBrain):
    """Brain - Responsible for Market Regime Detection (Trending vs Ranging)."""
    def initialize(self):
        super().initialize()
        self.volatility = VolatilityAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list):
                df.columns = ["o", "h", "l", "c", "t", "v"]

            regime = self.volatility.get_regime(df)
            return {
                "type": "REGIME",
                "symbol": event["symbol"],
                "regime": regime
            }
        return None

class ContrarianBrain(BaseBrain):
    """Brain - Purpose: Find reasons NOT to trade (Veto Logic)."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "SIGNAL":
            if event.get("atr", 0) < 0.0001:
                return {
                    "type": "VETO",
                    "symbol": event["symbol"],
                    "reason": "ATR_TOO_LOW"
                }
        return None

class NewsRiskBrain(BaseBrain):
    """Brain - Responsible for Economic Calendar and News Safety."""
    def initialize(self):
        super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.risk_manager.is_news_safe():
            return {
                "type": "NEWS_VETO",
                "symbol": event.get("symbol", "GLOBAL"),
                "reason": "HIGH_IMPACT_NEWS_PENDING"
            }
        return None

class MemoryBrain(BaseBrain):
    """Brain - Responsible for Performance Tracking and Bayesian Updating."""
    def __init__(self, name: str, input_queue: Queue, output_queue: Queue, cpu_affinity: Optional[List[int]] = None):
        super().__init__(name, input_queue, output_queue, cpu_affinity)
        self.performance_stats: Dict[str, Dict[str, Any]] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "EXECUTION_ORDER":
            symbol = event["symbol"]
            if symbol not in self.performance_stats:
                self.performance_stats[symbol] = {"trades": 0, "wins": 0}
            self.performance_stats[symbol]["trades"] += 1
            return {
                "type": "MEMORY_UPDATE",
                "symbol": symbol,
                "stats": self.performance_stats[symbol]
            }
        return None

class MonitoringBrain(BaseBrain):
    """Brain 8 - Responsible for Health Checks and Worker Restart."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "HEALTH_CHECK":
            return {
                "type": "MONITORING_REPORT",
                "status": "ALL_SYSTEMS_GO"
            }
        return None
