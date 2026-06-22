import asyncio
import logging
import pandas as pd
import numpy as np
import aiosqlite
import time
from typing import Dict, Any, Optional, List
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Market Data ingest and normalization."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP":
            return {
                "type": "MARKET_DATA", "symbol": event.get("s"), "bid": event.get("bi"), "ask": event.get("as"),
                "ltf": event.get("ltf", []), "h1": event.get("h1", []), "h4": event.get("h4", [])
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Technical Indicator Evidence."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            inds = self.analyst.calculate_all(df)
            rsi = inds["rsi"]
            evidence = {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "data": inds}
            if rsi > 60: evidence.update({"p_e_h": 0.65, "p_e": 0.50, "direction": 1})
            elif rsi < 40: evidence.update({"p_e_h": 0.65, "p_e": 0.50, "direction": -1})
            else: return None
            return evidence
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class TrendBrain(BaseBrain):
    """Brain 3 - 10503: Market Structure Evidence."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            struct = self.smc.detect_market_structure(df)
            h1_df = pd.DataFrame(event.get("h1", [])); h4_df = pd.DataFrame(event.get("h4", []))
            aligned = 0
            if not h1_df.empty:
                if isinstance(event["h1"][0], list): h1_df.columns = ["o", "h", "l", "c", "t", "v"]
                if self.smc.detect_market_structure(h1_df)["trend"] == struct["trend"]: aligned += 1
            if not h4_df.empty:
                if isinstance(event["h4"][0], list): h4_df.columns = ["o", "h", "l", "c", "t", "v"]
                if self.smc.detect_market_structure(h4_df)["trend"] == struct["trend"]: aligned += 1

            evidence = {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "direction": 1 if struct["trend"] == "BULLISH" else -1}
            if evidence["direction"] == 0: return None
            if aligned == 2: evidence.update({"p_e_h": 0.85, "p_e": 0.45})
            elif aligned == 1: evidence.update({"p_e_h": 0.70, "p_e": 0.55})
            else: evidence.update({"p_e_h": 0.60, "p_e": 0.60})
            return evidence
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class LiquidityBrain(BaseBrain):
    """Brain 4 - 10505: Order Block Evidence."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            obs = self.smc.detect_order_blocks(df)
            if not obs: return None
            latest_ob = obs[-1]
            return {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "direction": 1 if latest_ob["type"] == "BULLISH" else -1, "p_e_h": 0.80, "p_e": 0.60}
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class RegimeBrain(BaseBrain):
    """Brain - 10506: Volatility Regime Status."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.volatility = VolatilityAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            regime = self.volatility.get_regime(df)
            return {"type": "REGIME_STATUS", "symbol": event["symbol"], "source": self.name, "regime": regime}
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class ContrarianBrain(BaseBrain):
    """Brain - 10507: Veto logic."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            if event.get("atr", 0) < 0.00005:
                return {"type": "VETO", "symbol": event["symbol"], "reason": "ATR_TOO_LOW"}
        return None

class NewsRiskBrain(BaseBrain):
    """Brain - 10509: News safety veto."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.risk_manager.is_news_safe():
            return {"type": "NEWS_VETO", "symbol": event.get("symbol", "GLOBAL"), "reason": "NEWS_WINDOW"}
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class MemoryBrain(BaseBrain):
    """Brain - 12501: Continuous Learning and Calibration."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.db_path = "audit_records.db"
        self.reliabilities: Dict[str, float] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        e_type = event.get("type")

        # 12502: Record trade outcome and update reliabilities
        if e_type == "TRADE_CLOSED":
            symbol = event["symbol"]; outcome = event["outcome"] # WIN/LOSS
            evidence_trail = event.get("evidence_trail", [])

            async with aiosqlite.connect(self.db_path) as db:
                for entry in evidence_trail:
                    source = entry["source"]
                    correct = (entry["direction"] == 1 and outcome == "WIN") or (entry["direction"] == -1 and outcome == "WIN")
                    # Simplified Bayesian weight update: P(H|E) = (P(E|H)*P(H))/P(E)
                    # Here we adjust the reliability score
                    curr = self.reliabilities.get(source, 1.0)
                    adjustment = 0.05 if correct else -0.05
                    self.reliabilities[source] = max(0.1, min(2.0, curr + adjustment))

                    await db.execute("INSERT INTO brain_performance (source, outcome, timestamp) VALUES (?, ?, ?)", (source, outcome, time.time()))
                await db.commit()

            # Broadcast updated reliabilities
            return {"type": "RELIABILITY_REPORT", "scores": self.reliabilities}

        elif e_type == "RELIABILITY_REQUEST":
            return {"type": "RELIABILITY_REPORT", "scores": self.reliabilities}

        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class RiskBrain(BaseBrain):
    """Brain 6 - 10512: Probabilistic Position Sizing."""
    async def initialize(self):
        await super().initialize()
        await self._init_perf_db()
        self.risk_manager = RiskManager(load_config())
        self.execution_score = 0.95

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]; prob = event["probability"]
            if prob < 0.55: return None
            regime_score = 1.0 if event.get("regime") == "TRENDING" else (0.8 if event.get("regime") == "NORMAL" else 0.5)
            v = self.risk_manager.validate_trade(symbol, event["action"], 1000.0, atr=event["atr"])
            if v["safe"]:
                prob_mult = (prob - 0.50) / 0.45
                final_lots = round(v["lots"] * prob_mult * regime_score * self.execution_score, 2)
                if final_lots < 0.01: return None
                return {"type": "VALIDATED_TRADE", "symbol": symbol, "action": event["action"], "lots": final_lots, "sl_pts": v["sl_pts"], "tp_pts": v["tp_pts"], "probability": prob, "evidence_trail": event.get("evidence_trail", [])}
        return None

    async def _init_perf_db(self):
        self.db_path = "audit_records.db"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS brain_performance (source TEXT, outcome TEXT, timestamp REAL)")
            await db.commit()

class ExecutionBrain(BaseBrain):
    """Brain 7 - 10513: Actuation."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            logger.info(f"Bayesian Actuation: {event['action']} {event['symbol']} P={event['probability']:.2f}")
            return {
                "type": "EXECUTION_ORDER",
                "t": "DEC",
                "id": int(time.time()),
                "s": event["symbol"],
                "act": event["action"],
                "lts": event["lots"],
                "sl_p": event["sl_pts"],
                "tp_p": event["tp_pts"],
                "evidence_trail": event.get("evidence_trail")
            }
        return None

class AnomalyBrain(BaseBrain):
    """Brain 8 - 10514: Flash Crash and Spike Detection."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty or len(df) < 2: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

            price_change_pct = abs(df['c'].iloc[-1] - df['o'].iloc[-1]) / df['o'].iloc[-1]
            if price_change_pct > 0.02: # 2% move in one bar
                logger.warning(f"ANOMALY: Flash spike detected on {event['symbol']}")
                return {"type": "ANOMALY_STATUS", "symbol": event["symbol"], "anomaly": "SPIKE", "severity": "HIGH"}
        return None

class PortfolioBrain(BaseBrain):
    """Brain 9 - 10515: Global Risk and Capital Allocation."""
    async def initialize(self):
        await super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "HB":
            equity = event.get("e", 0)
            drawdown = event.get("d", 0)
            if drawdown > self.risk_manager.config.risk.max_drawdown_pct:
                logger.critical("PORTFOLIO: Global Drawdown Threshold Breached!")
                return {"type": "VETO", "symbol": "GLOBAL", "reason": "MAX_DRAWDOWN"}
        return None

class MonitoringBrain(BaseBrain):
    """Brain 10 - 10516: System Health and Latency Tracking."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "HEALTH_CHECK":
            return {"type": "HEALTH_REPORT", "status": "OPTIMAL", "timestamp": time.time()}
        return None
