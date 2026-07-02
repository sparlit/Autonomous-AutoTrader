import asyncio
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.hive.config import load_config
from src.python.execution.risk_manager import RiskManager

try:
    import aat_institutional_core as aat_rust
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Market Data ingestion and normalization."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA_RAW":
            symbol = event.get("s")
            bid, ask = event.get("b", 0), event.get("a", 0)

            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "spread": event.get("sp", 0),
                "tick_val": event.get("tv", 10.0),
                "tick_size": event.get("ts", 0.0001),
                "last_update": time.time()
            })

            return {"type": "MARKET_DATA", "symbol": symbol, "bid": bid, "ask": ask,
                    "atr": event.get("atr", 0), "ltf": event.get("ltf", []),
                    "m15": event.get("m15", []), "h1": event.get("h1", []),
                    "h4": event.get("h4", []), "d1": event.get("d1", [])}
        return None

class TrendBrain(BaseBrain):
    """
    Brain 3 - 10503: Multi-Timeframe Trend Evidence (V3.3.0-ASCENDANT).
    Mandatory: M15, H1, H4, D1.
    Rule: Majority (confluence) provided the TFs are consecutive.
    """
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            symbol = event["symbol"]

            tfs = ["m15", "h1", "h4", "d1"]
            trends = {}

            for tf in tfs:
                df = pd.DataFrame(event.get(tf, []))
                if not df.empty:
                    if isinstance(event[tf][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
                    trends[tf] = self.smc.detect_market_structure(df)["trend"]
                else:
                    trends[tf] = "NEUTRAL"

            # Check consecutive majority
            # M15-H1, H1-H4, H4-D1
            bullish_pairs = 0
            bearish_pairs = 0

            if trends["m15"] == "BULLISH" and trends["h1"] == "BULLISH": bullish_pairs += 1
            if trends["h1"] == "BULLISH" and trends["h4"] == "BULLISH": bullish_pairs += 1
            if trends["h4"] == "BULLISH" and trends["d1"] == "BULLISH": bullish_pairs += 1

            if trends["m15"] == "BEARISH" and trends["h1"] == "BEARISH": bearish_pairs += 1
            if trends["h1"] == "BEARISH" and trends["h4"] == "BEARISH": bearish_pairs += 1
            if trends["h4"] == "BEARISH" and trends["d1"] == "BEARISH": bearish_pairs += 1

            direction = 0
            p_e_h = 0.50
            if bullish_pairs >= 2: direction = 1; p_e_h = 0.85
            elif bearish_pairs >= 2: direction = -1; p_e_h = 0.85
            elif bullish_pairs == 1: direction = 1; p_e_h = 0.70
            elif bearish_pairs == 1: direction = -1; p_e_h = 0.70

            # Set global trend for orchestrator
            self.ipc.set_state(f"trend_stats:{symbol}", trends)

            return {
                "type": "EVIDENCE", "symbol": symbol, "source": self.name,
                "direction": direction, "p_e_h": p_e_h, "p_e": 0.50,
                "data": {"trends": trends}
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Technical Indicator Evidence."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

            rsi = self.analyst.calculate_rsi(df)
            ema_fast = self.analyst.calculate_ema(df, 9)
            ema_slow = self.analyst.calculate_ema(df, 21)

            direction = 0
            if rsi > 55 and ema_fast > ema_slow: direction = 1
            elif rsi < 45 and ema_fast < ema_slow: direction = -1

            return {
                "type": "EVIDENCE", "symbol": event["symbol"], "source": self.name,
                "direction": direction, "p_e_h": 0.75, "p_e": 0.50,
                "data": {"rsi": rsi, "atr": event.get("atr", 0)}
            }
        return None

class RiskBrain(BaseBrain):
    """Brain 11 - 10517: Local Risk Vetting and Threshold Enforcement."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            # Rule: 0.01 lots strictly enforced
            event["lots"] = 0.01

            # Rule: Mandatory Trend Alignment
            # (Handled in MetaBrain, but we can double check here)
            return {"type": "VALIDATED_TRADE", **event}
        return None

class ExecutionBrain(BaseBrain):
    """Brain 12 - 10512: Final Order formatting for MT5."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            return {
                "type": "EXECUTION_ORDER", "t": "DEC", "s": event["symbol"],
                "act": event["action"], "lts": 0.01, # Strict 0.01 lots
                "sl_p": 0, "tp_p": 0, # Will be calculated by RiskManager in Orchestrator
                "reason": event.get("reason", "BRAIN_SIGNAL")
            }
        return None

class AnomalyBrain(BaseBrain):
    """Brain 8 - 10508: Anomaly detection."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            price_change_pct = abs(df['c'].iloc[-1] - df['o'].iloc[-1]) / df['o'].iloc[-1]
            if price_change_pct > 0.02:
                return {"type": "ANOMALY_STATUS", "symbol": event["symbol"], "anomaly": "SPIKE", "severity": "HIGH"}
        return None

class PortfolioBrain(BaseBrain):
    """Brain 9 - 10515: Global Risk and Capital Allocation."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MonitoringBrain(BaseBrain):
    """Brain 10 - 10516: System Health Monitoring."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class LiquidityBrain(BaseBrain):
    """Brain 5 - 10505: Liquidity hunt detection."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class RegimeBrain(BaseBrain):
    """Brain 6 - 10506: Market Regime classification."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            return {"type": "REGIME_STATUS", "symbol": event["symbol"], "source": self.name, "regime": "TRENDING"}
        return None

class ContrarianBrain(BaseBrain):
    """Brain 7 - 10507: Contrarian signal detection."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class NewsRiskBrain(BaseBrain):
    """Brain 15 - 10521: News Impact analysis."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MemoryBrain(BaseBrain):
    """Brain 16 - 10522: Historical trade memory."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class CorrelationBrain(BaseBrain):
    """Brain 14 - 10519: Cross-symbol correlation analysis."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class SwingMaster(BaseBrain):
    """Strategy: Swing Trading."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class ScalpMaster(BaseBrain):
    """Strategy: Scalping."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class VSAMaster(BaseBrain):
    """Strategy: Volume Spread Analysis."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class WyckoffMaster(BaseBrain):
    """Strategy: Wyckoff Method."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class ICTKillzone(BaseBrain):
    """Strategy: ICT Killzones."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MomentumBrain(BaseBrain):
    """Brain 4 - 10504: Momentum analysis."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class StructureBrain(BaseBrain):
    """Brain 13 - 10518: SMC Structural Elements."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
