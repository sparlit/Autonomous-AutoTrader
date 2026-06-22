import asyncio
import logging
import os
import psutil
import time
import signal
import ujson as json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from multiprocessing import Process
from pydantic import BaseModel
from fakeredis import FakeRedis

logger = logging.getLogger("AAT_BaseBrain")

class SignalPayload(BaseModel):
    """12000: Standardized strategy signal output."""
    symbol: str
    timeframe: int
    direction: int
    confidence: float
    strategy_name: str
    magic: int

class BrainContract(ABC):
    """The strict contract every Brain must follow."""
    @abstractmethod
    async def initialize(self):
        """12001: Hardware and dependency setup."""
        raise NotImplementedError()
    @abstractmethod
    def run(self):
        """12002: Process main event loop."""
        raise NotImplementedError()
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """12003: Collect process health metrics."""
        raise NotImplementedError()

class BaseBrain(Process, BrainContract):
    """
    12004: Foundation class for isolated brain processes.
    Reinforced with execution timeouts and bounded stream management.
    """

    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None):
        Process.__init__(self)
        self.name = name
        self.cpu_affinity = cpu_affinity
        self.is_running = True
        self._last_heartbeat = time.time()
        self._processed_count = 0
        self._latency_sum = 0.0
        self.redis = None # Initialized in child process
        self.max_execution_time = 0.1 # 100ms hard deadline (12101)
        self.stream_max_len = 1000 # Bounded streams to prevent OOM (12102)

    async def initialize(self):
        """12005: Hardware and dependency setup."""
        self.redis = FakeRedis()
        p = psutil.Process(os.getpid())
        if self.cpu_affinity:
            try:
                p.cpu_affinity(self.cpu_affinity)
                logger.info(f"Brain {self.name} pinned to cores: {self.cpu_affinity}")
            except Exception as e:
                logger.warning(f"Affinity fail for {self.name}: {e}")

        logging.basicConfig(level=logging.INFO, format=f"%(asctime)s - {self.name} - %(levelname)s - %(message)s")
        logger.info(f"Brain {self.name} online (PID {os.getpid()})")

    def run(self):
        """12006: Process entry point."""
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)
        asyncio.run(self._async_run())

    async def _async_run(self):
        """Internal async entry point to ensure loop is running for initialization."""
        await self.initialize()
        await self._main_loop()

    async def _main_loop(self):
        """12007: Async execution loop with timeouts and backpressure."""
        stream_name = f"stream:{self.name}"
        while self.is_running:
            try:
                # 12103: Drop old ticks if backlog exists (Coalescing/Backpressure)
                messages = self.redis.xread({stream_name: '0'}, count=10, block=1)
                if messages:
                    for stream, msgs in messages:
                        # Only process the LATEST message if it's high-frequency data
                        # to ensure low-latency execution (12104)
                        latest_msg = msgs[-1]
                        msg_id, data = latest_msg

                        event = json.loads(data[b'payload'])
                        start_time = time.perf_counter()

                        try:
                            # 12105: Hard execution deadline
                            result = await asyncio.wait_for(self.process(event), timeout=self.max_execution_time)
                            if result: self.publish(result)
                        except asyncio.TimeoutError:
                            logger.error(f"Brain {self.name} TIMEOUT on msg {msg_id}. Dropping result.")

                        # 12106: Explicitly clear processed items
                        for m_id, _ in msgs:
                            self.redis.xdel(stream_name, m_id)

                        self._latency_sum += (time.perf_counter() - start_time)
                        self._processed_count += 1
                else:
                    await asyncio.sleep(0.0001) # Yield to CPU
            except Exception as e:
                logger.error(f"Brain {self.name} Error: {e}")
                await asyncio.sleep(0.1)

    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """12009: Domain-specific logic."""
        raise NotImplementedError()

    def publish(self, result: Dict[str, Any]):
        """12010: Publish to the Orchestrator stream with bounded length."""
        result['source'] = self.name; result['timestamp'] = time.time()
        payload = json.dumps(result)
        # 12107: Use MAXLEN for backpressure in message bus
        self.redis.xadd("stream:orchestrator", {"payload": payload}, maxlen=self.stream_max_len)

    def health(self) -> Dict[str, Any]:
        """12011: Collect health metrics."""
        p = psutil.Process(os.getpid()); avg_latency = self._latency_sum / self._processed_count if self._processed_count > 0 else 0
        return {"name": self.name, "pid": os.getpid(), "cpu": p.cpu_percent(), "mem": p.memory_info().rss / 1024 / 1024, "count": self._processed_count, "latency": avg_latency * 1000}

    def _handle_exit(self, signum, frame):
        self.is_running = False
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
            evidence = {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "direction": 1 if struct["trend"] == "BULLISH" else (-1 if struct["trend"] == "BEARISH" else 0)}
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
            return {"type": "EXECUTION_ORDER", "symbol": event["symbol"], "action": event["action"], "lots": event["lots"], "sl": event["sl_pts"], "tp": event["tp_pts"], "evidence_trail": event.get("evidence_trail")}
        return None

class AnomalyBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
class PortfolioBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
class MonitoringBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from src.python.brains.base import BaseBrain
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst

logger = logging.getLogger("AAT_MetaBrain")

class MetaBrain(BaseBrain):
    """
    Brain 11 - 10601: The Bayesian Probability Engine.
    Self-Learning: Adjusts evidence weights based on brain reliability reports.
    Explainability: Returns detailed impact of each brain on final posterior.
    """
    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, threshold: float = 0.70):
        super().__init__(name, cpu_affinity)
        self.threshold = threshold
        self.symbol_state: Dict[str, Dict[str, Any]] = {}
        self.brain_reliability: Dict[str, float] = {}
        self.required_sources = ["Trend_1", "Indicator_1", "Liquidity_1", "Regime_1"]

    async def initialize(self):
        await super().initialize()
        # Additional async initialization if needed

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        symbol = event.get("symbol")
        if not symbol: return None
        if symbol not in self.symbol_state: self.symbol_state[symbol] = self._new_state()
        state = self.symbol_state[symbol]; e_type = event.get("type")
        if e_type == "MARKET_DATA_REFRESH": self.symbol_state[symbol] = self._new_state(); return None
        if e_type == "RELIABILITY_REPORT": self.brain_reliability = event.get("scores", {}); return None
        if e_type == "REGIME_STATUS": state["regime"] = event["regime"]; state["received_sources"].add(event["source"])
        elif e_type in ["VETO", "NEWS_VETO"]: state["veto"] = True; state["veto_reason"] = event.get("reason")
        elif e_type == "EVIDENCE":
            p_e_h = event.get("p_e_h", 0.50); p_e = event.get("p_e", 0.50)
            rel = self.brain_reliability.get(event["source"], 1.0)
            # 12601: Reliability-weighted evidence
            weighted_p_e_h = 0.50 + (p_e_h - 0.50) * rel
            prior = state["prior"]; posterior = (weighted_p_e_h * prior) / p_e
            impact = posterior - prior
            state["prior"] = max(0.01, min(0.99, posterior))
            # 12602: Rich explainability trail
            state["evidence_trail"].append({"source": event["source"], "direction": event.get("direction", 0), "posterior": state["prior"], "impact": impact, "reliability": rel})
            state["received_sources"].add(event["source"])
            if "data" in event:
                state["atr"] = event["data"].get("atr", state["atr"]); state["rsi"] = event["data"].get("rsi", state["rsi"])
        if all(src in state["received_sources"] for src in self.required_sources):
            if state["prior"] >= self.threshold and not state["veto"]:
                action = self._determine_direction(state)
                if action != "WAIT":
                    res = {
                        "type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": action,
                        "probability": state["prior"], "regime": state["regime"], "atr": state["atr"], "rsi": state["rsi"],
                        "evidence_trail": state["evidence_trail"],
                        # 12603: Detailed explainability summary
                        "explainability": [f"{e['source']} ({e['reliability']:.2f}): {'+' if e['impact'] >= 0 else ''}{e['impact']:.2f} -> P={e['posterior']:.2f}" for e in state['evidence_trail']]
                    }
                    state["received_sources"] = set(); return res
        return None

    def _new_state(self):
        return {"prior": 0.50, "evidence_trail": [], "regime": "NORMAL", "veto": False, "received_sources": set(), "atr": 0.0, "rsi": 50}

    def _determine_direction(self, state):
        directions = [e["direction"] for e in state["evidence_trail"] if e["direction"] != 0]
        if not directions: return "WAIT"
        net_dir = sum(directions); return "BUY" if net_dir > 0 else ("SELL" if net_dir < 0 else "WAIT")

class ConsensusEngine:
    """30001: Legacy Consensus Engine for synchronous worker processing."""
    def __init__(self):
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()
        self._thread_pool = ThreadPoolExecutor(max_workers=8)
        self.magic = 30001

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hist_data = data.get("history", [])
        if hist_data and isinstance(hist_data[0], list): hist_data = self._parse_history(hist_data)
        if not hist_data: return {"act": "WAIT", "reason": "EMPTY_HIST", "m_id": 30003}

        df = pd.DataFrame(hist_data)
        inds = self.indicators.calculate_all(df)
        atr = inds.get("atr", 0.0)
        vsa = self.volatility.analyze_vsa(df)
        trigger = self.smc.detect_candlestick_trigger(df)

        from src.python.brains.strategies.swing_master import SwingMaster
        from src.python.brains.strategies.day_master import DayMaster
        from src.python.brains.strategies.carry_master import CarryMaster
        from src.python.brains.strategies.scalp_master import ScalpMaster

        strats = [SwingMaster("S"), DayMaster("D"), CarryMaster("C"), ScalpMaster("SC")]
        strat_results = [asyncio.run(s.process(data)) for s in strats]

        votes = [r for r in strat_results if r and r.direction != 0]
        net_direction = sum(v.direction for v in votes)
        regime = self.volatility.get_regime(df)

        action = "WAIT"
        if net_direction >= 2: action = "BUY"
        elif net_direction <= -2: action = "SELL"

        return {
            "act": action,
            "scr": net_direction,
            "atr": atr,
            "vsa": vsa,
            "regime": regime,
            "m_id": 30003,
            "magic": self.magic
        }
