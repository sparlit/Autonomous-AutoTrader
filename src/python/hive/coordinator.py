import asyncio
import logging
import ujson as json
import datetime
import time
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.base import BrainRegistry
from src.python.execution.risk_manager import RiskManager
from src.python.execution.ledger import TradeLedger
from src.python.execution.manager import PositionManager
from src.python.brains.worker import process_task, worker_init

logger = logging.getLogger("AAT_Coordinator")

class HiveCoordinator:
    def __init__(self):
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
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.cooldowns: Dict[str, datetime.datetime] = {}
        self._initialize_brains()

    def _initialize_brains(self):
        from src.python.brains.specialized import HTFAnalysisBrain, LTFTriggerBrain, DecisionBrain, CorrelationBrain
        self.registry.register(HTFAnalysisBrain("HTF_Analyst"))
        self.registry.register(LTFTriggerBrain("LTF_Trigger"))
        self.registry.register(DecisionBrain("Decision_Maker"))
        self.corr_brain = CorrelationBrain("Correlation_Analyst")

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "PNG": return {"type": "PING"}
        if m_type == "HB":
            return {"type": "HEARTBEAT", "symbol": message.get("s"), "equity": message.get("e"), "drawdown": message.get("d")}
        if m_type == "T_ACK":
            return {"type": "TRADE_ACK", "id": message.get("id"), "ticket": message.get("tk"), "err": message.get("err")}
        if m_type == "SYNC":
            return {"type": "SYNC", "symbol": message.get("s"), "tickets": message.get("tk", [])}
        return message

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        raw_msg = message
        message = self._normalize_message(message)
        msg_type = message.get("type")

        if msg_type == "PING": return {"t": "PNG_ACK"}

        if msg_type == "HEARTBEAT":
            symbol = message.get("symbol", "UNKNOWN")
            equity = float(message.get("equity", 0.0))
            await self.ledger.update_peak_equity(equity)
            self.risk_manager.peak_equity = await self.ledger.get_peak_equity()
            self.agent_states[client_id] = {"symbol": symbol, "last_seen": time.time(), "equity": equity}
            return {"t": "HB_ACK"}

        if msg_type == "SYNC":
            symbol = message.get("symbol")
            mt5_tickets = set(message.get("tickets", []))
            active_trades = await self.ledger.get_active_trades(symbol)
            for trade in active_trades:
                if trade["ticket"] not in mt5_tickets:
                    await self.ledger.close_trade(trade["ticket"])
                    self.cooldowns[symbol] = datetime.datetime.now() + datetime.timedelta(hours=4)
                    logger.info(f"Hybrid Sync: Closed trade {trade['ticket']} detected. 4h Cooldown for {symbol}")
            return {"t": "SYNC_ACK"}

        if msg_type == "TRADE_ACK":
            internal_id = message.get("id"); ticket = message.get("ticket"); err = message.get("err")
            if ticket and ticket > 0: await self.ledger.update_execution(internal_id, ticket, "OPEN")
            else: await self.ledger.update_execution(internal_id, 0, f"FAILED: {err}")
            return {"t": "ACK"}

        if raw_msg.get("t") == "DP":
            symbol = raw_msg.get("s")
            equity = self.agent_states.get(client_id, {}).get("equity", 1000.0)
            bid = raw_msg.get("bi", 0.0); ask = raw_msg.get("as", 0.0)

            # --- HYBRID PATH A: LIZARD BRAIN (SEQUENTIAL VETOES) ---
            # Direct async checks
            if not self.risk_manager.is_session_active() or not self.risk_manager.is_news_safe():
                return {"t": "DEC", "s": symbol, "act": "WAIT", "msg": "VETO_RISK"}

            # --- HYBRID PATH B: CEREBRAL BRAIN (PARALLEL DEEP-PATH) ---
            loop = asyncio.get_event_loop()
            try:
                analysis = await loop.run_in_executor(self.executor, process_task, raw_msg)
            except Exception as e:
                logger.error(f"Strategy Worker Error: {e}")
                return {"t": "DEC", "s": symbol, "act": "WAIT", "msg": "WORKER_ERR"}

            atr = analysis.get("atr", 0.0)
            mgmt_commands = await self.pos_manager.monitor_and_manage(symbol, (bid+ask)/2, atr)

            response = {"t": "DEC", "s": symbol, "act": "WAIT"}
            if mgmt_commands: response["mgmt"] = mgmt_commands
            if "draw" in analysis: response["drw"] = analysis["draw"]

            if analysis.get("action") in ["BUY", "SELL"]:
                action = analysis["action"]
                if symbol in self.cooldowns and datetime.datetime.now() < self.cooldowns[symbol]: return response

                active_trades = await self.ledger.get_active_trades()
                if not self.corr_brain.check_exposure(symbol, action, active_trades)["safe"]: return response

                validation = self.risk_manager.validate_trade(
                    symbol, action, equity, atr=atr,
                    tick_val=raw_msg.get("tv", 10.0), tick_size=raw_msg.get("ts", 0.0001)
                )
                if validation["safe"]:
                    internal_id = await self.ledger.record_intent(symbol, action, validation["lots"], validation["sl_pts"], validation["tp_pts"])
                    response.update({"id": internal_id, "act": action, "lts": validation["lots"], "sl_p": validation["sl_pts"], "tp_p": validation["tp_pts"]})
            return response

        return {"t": "ACK", "m": f"Processed {msg_type}"}

    async def run(self):
        logger.info("Starting Hybrid Parallel Coordinator...")
        await self.ledger.init_db()
        self.risk_manager.peak_equity = await self.ledger.get_peak_equity()
        await self.server.start()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
