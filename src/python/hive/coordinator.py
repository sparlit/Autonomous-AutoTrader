import asyncio
import logging
import ujson as json
import datetime
import time
import os
import sys
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.base import BrainRegistry
from src.python.execution.risk_manager import RiskManager
from src.python.execution.ledger import TradeLedger
from src.python.execution.manager import PositionManager
from src.python.brains.worker import process_task, worker_init
from src.python.bridge.watchdog import SystemWatchdog
from src.python.brains.specialized import ContextBrain

# Import Rust Core
sys.path.append(os.path.join(os.path.dirname(__file__), '../bridge'))
try:
    import aat_rust_core
    RUST_CORE_ENABLED = True
except ImportError:
    RUST_CORE_ENABLED = False

logger = logging.getLogger("AAT_Coordinator")

class HiveCoordinator:
    def __init__(self):
        """Magic: 10201"""
        self.config = load_config()
        self.server = BridgeServer(
            self.config.bridge.host,
            self.config.bridge.port,
            self.handle_message
        )
        self.registry = BrainRegistry()
        self.risk_manager = RiskManager(self.config)
        self.ledger = TradeLedger()
        self.pos_manager = PositionManager(self.ledger)

        self.executor = ProcessPoolExecutor(
            max_workers=self.config.brains.parallel_workers,
            initializer=worker_init
        )
        self.io_pool = ThreadPoolExecutor(max_workers=10)

        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.watchdog = SystemWatchdog(self.agent_states, self.config.bridge.timeout)
        self.context_brain = ContextBrain("Context_Analyst")
        self.cooldowns: Dict[str, datetime.datetime] = {}
        self.symbol_locks: Dict[str, asyncio.Lock] = {}
        self._initialize_brains()

    def _initialize_brains(self):
        """Magic: 10202"""
        from src.python.brains.specialized import HTFAnalysisBrain, LTFTriggerBrain, DecisionBrain, CorrelationBrain
        from src.python.brains.strategies.swing_master import SwingMaster
        from src.python.brains.strategies.day_master import DayMaster
        from src.python.brains.strategies.carry_master import CarryMaster
        from src.python.brains.strategies.scalp_master import ScalpMaster

        self.registry.register(HTFAnalysisBrain("HTF_Analyst"))
        self.registry.register(LTFTriggerBrain("LTF_Trigger"))
        self.registry.register(DecisionBrain("Decision_Maker"))

        # Strategy Suite
        self.registry.register(SwingMaster("Swing_Master"))
        self.registry.register(DayMaster("Day_Master"))
        self.registry.register(CarryMaster("Carry_Master"))
        self.registry.register(ScalpMaster("Scalp_Master"))

        self.corr_brain = CorrelationBrain("Correlation_Analyst")

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 10203"""
        m_type = message.get("t")
        if m_type == "PNG": return {"type": "PING"}
        if m_type == "HB":
            return {"type": "HEARTBEAT", "symbol": message.get("s"), "equity": message.get("e"), "drawdown": message.get("d")}
        if m_type == "DP": return message
        if m_type == "T_ACK":
            return {"type": "TRADE_ACK", "id": message.get("id"), "ticket": message.get("tk"), "err": message.get("err")}
        if m_type == "SYNC":
            return {"type": "SYNC", "symbol": message.get("s"), "tickets": message.get("tk", [])}
        return message

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 10204"""
        raw_msg = message; m_type = raw_msg.get("t")
        if m_type == "PNG":
            if "client_t" in raw_msg: self.watchdog.record_rtt(client_id, raw_msg["client_t"])
            return {"t": "PNG_ACK"}
        if m_type == "HB":
            equity = float(raw_msg.get("e", 0.0)); await self.ledger.update_peak_equity(equity)
            self.agent_states[client_id] = {"symbol": raw_msg.get("s"), "last_seen": time.time(), "equity": equity}
            return {"t": "HB_ACK"}
        if m_type == "DP":
            symbol = raw_msg.get("s")
            if symbol not in self.symbol_locks: self.symbol_locks[symbol] = asyncio.Lock()
            async with self.symbol_locks[symbol]: return await self.process_data_push(client_id, raw_msg)

        norm_message = self._normalize_message(message); msg_type = norm_message.get("type")
        if msg_type == "SYNC":
            symbol = norm_message.get("symbol"); mt5_tickets = set(norm_message.get("tickets", []))
            active_trades = await self.ledger.get_active_trades_db(symbol)
            ledger_tickets = {t["ticket"] for t in active_trades}
            for trade in active_trades:
                if trade["ticket"] not in mt5_tickets:
                    await self.ledger.close_trade(trade["ticket"])
                    self.cooldowns[symbol] = datetime.datetime.now() + datetime.timedelta(hours=4)
            for tk in mt5_tickets:
                if tk not in ledger_tickets:
                    await self.ledger.adopt_trade(tk, symbol)
            return {"t": "SYNC_ACK"}
        if msg_type == "TRADE_ACK":
            internal_id = norm_message.get("id"); ticket = norm_message.get("ticket"); price = norm_message.get("price"); err = norm_message.get("err")
            if ticket and ticket > 0: await self.ledger.update_execution(internal_id, ticket, price, "OPEN")
            else: await self.ledger.update_execution(internal_id, 0, f"FAILED: {err}")
            return {"t": "ACK"}
        return {"t": "ACK", "m": f"Processed {m_type}"}

    async def process_data_push(self, client_id: str, raw_msg: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 10205"""
        symbol = raw_msg.get("s"); equity = self.agent_states.get(client_id, {}).get("equity", 1000.0)
        bid = raw_msg.get("bi", 0.0); ask = raw_msg.get("as", 0.0)

        ctx = self.context_brain.global_context
        if ctx.get("news_high_impact") or not self.risk_manager.is_session_active() or not self.risk_manager.is_news_safe():
            return {"t": "DEC", "s": symbol, "act": "WAIT", "m": "VETO"}

        loop = asyncio.get_event_loop()
        try:
            analysis = await loop.run_in_executor(self.executor, process_task, raw_msg)
        except Exception as e:
            logger.error(f"Worker Failure for {symbol}: {e}. Restarting Pool.")
            self.executor.shutdown(wait=False); self.executor = ProcessPoolExecutor(max_workers=self.config.brains.parallel_workers, initializer=worker_init)
            return {"t": "DEC", "s": symbol, "act": "WAIT", "m": "RECOVERY"}

        atr = analysis.get("atr", 0.0); mgmt = await self.pos_manager.monitor_and_manage(symbol, (bid+ask)/2, atr)

        response = {
            "t": "DEC", "s": symbol, "act": "WAIT",
            "tlm": {
                "scr": analysis.get("scr", 0),
                "htf": analysis.get("htf", "NEUTRAL"),
                "st": "HEALTHY",
                "dd": round((self.risk_manager.peak_equity - equity)/self.risk_manager.peak_equity*100, 2) if self.risk_manager.peak_equity > 0 else 0
            }
        }
        if mgmt: response["mgmt"] = mgmt
        if "draw" in analysis: response["drw"] = analysis["draw"]

        if analysis.get("act") in ["BUY", "SELL"]:
            action = analysis["act"]
            if symbol in self.cooldowns and datetime.datetime.now() < self.cooldowns[symbol]: return response
            active_trades = self.ledger.get_cached_active_trades()

            if RUST_CORE_ENABLED:
                exposures = [t.get("lots", 0.01) for t in active_trades]
                vols = [0.002 for _ in active_trades]
                total_var = aat_rust_core.calculate_var_parallel(exposures, vols)
                if total_var > 5.0:
                    logger.warning(f"VETO: VaR limit exceeded ({total_var:.2f})")
                    return response

            if not self.corr_brain.check_exposure(symbol, action, active_trades)["safe"]: return response

            v = self.risk_manager.validate_trade(symbol, action, equity, atr=atr, tick_val=raw_msg.get("tv", 10.0), tick_size=raw_msg.get("ts", 0.0001))
            if v["safe"]:
                internal_id = await self.ledger.record_intent(symbol, action, v["lots"], 0, 0)
                response["act"] = action
                response["id"] = internal_id
                response["lts"] = v["lots"]
                response["sl_p"] = v["sl_pts"]
                response["tp_p"] = v["tp_pts"]

        return response

    async def run(self):
        """Magic: 10206"""
        logger.info("Starting Multi-Paradigm Hybrid Coordinator...")
        await self.ledger.init_db()
        self.risk_manager.peak_equity = self.ledger.get_cached_peak_equity()
        asyncio.create_task(self.watchdog.run()); asyncio.create_task(self.context_brain.update_global_context())
        await self.server.start()
