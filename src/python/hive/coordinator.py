import asyncio
import logging
import ujson as json
import datetime
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.base import BrainRegistry
from src.python.execution.risk_manager import RiskManager
from src.python.execution.ledger import TradeLedger
from src.python.execution.manager import PositionManager
from src.python.brains.consensus import ConsensusEngine
from src.python.brains.specialized import CorrelationBrain

logger = logging.getLogger("AAT_Coordinator")

def process_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    engine = ConsensusEngine()
    return engine.analyze_sync(data)

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
        self.corr_brain = CorrelationBrain("Correlation_Analyst")
        self.executor = ProcessPoolExecutor(max_workers=self.config.brains.parallel_workers)
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.cooldowns: Dict[str, datetime.datetime] = {}
        self._initialize_brains()

    def _initialize_brains(self):
        from src.python.brains.specialized import HTFAnalysisBrain, LTFTriggerBrain, DecisionBrain
        self.registry.register(HTFAnalysisBrain("HTF_Analyst"))
        self.registry.register(LTFTriggerBrain("LTF_Trigger"))
        self.registry.register(DecisionBrain("Decision_Maker"))

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "PNG": return {"type": "PING"}
        if m_type == "HB":
            return {"type": "HEARTBEAT", "symbol": message.get("s"), "equity": message.get("e"), "drawdown": message.get("d")}
        if m_type == "DP":
            return {
                "type": "DATA_PUSH", "symbol": message.get("s"), "tf": message.get("tf"),
                "history": self._parse_history(message.get("ltf", [])),
                "h1": self._parse_history(message.get("h1", [])),
                "h4": self._parse_history(message.get("h4", [])),
                "bid": message.get("bi"), "ask": message.get("as"),
                "tick_val": message.get("tv"), "tick_size": message.get("ts")
            }
        if m_type == "T_ACK":
            return {"type": "TRADE_ACK", "id": message.get("id"), "ticket": message.get("tk"), "err": message.get("err")}
        if m_type == "SYNC":
            return {"type": "SYNC", "symbol": message.get("s"), "tickets": message.get("tk", [])}
        return message

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        message = self._normalize_message(message)
        msg_type = message.get("type")

        if msg_type == "PING": return {"t": "PNG_ACK"}

        if msg_type == "HEARTBEAT":
            symbol = message.get("symbol", "UNKNOWN")
            self.agent_states[client_id] = {
                "symbol": symbol,
                "last_seen": asyncio.get_event_loop().time(),
                "status": "HEALTHY",
                "equity": float(message.get("equity", 0.0)),
                "drawdown": float(message.get("drawdown", 0.0))
            }
            return {"t": "HB_ACK"}

        if msg_type == "SYNC":
            symbol = message.get("symbol")
            mt5_tickets = set(message.get("tickets", []))
            active_trades = await self.ledger.get_active_trades(symbol)
            for trade in active_trades:
                if trade["ticket"] not in mt5_tickets:
                    # Reconciliation: Assume SL hit if closed and last price was near SL
                    await self.ledger.close_trade(trade["ticket"])
                    self.cooldowns[symbol] = datetime.datetime.now() + datetime.timedelta(hours=4)
                    logger.info(f"Synchronized closed trade: {trade['ticket']}. 4h Cooldown activated for {symbol}")
            return {"t": "SYNC_ACK"}

        if msg_type == "TRADE_ACK":
            internal_id = message.get("id")
            ticket = message.get("ticket")
            err = message.get("err")
            if ticket and ticket > 0:
                await self.ledger.update_execution(internal_id, ticket, "OPEN")
            else:
                await self.ledger.update_execution(internal_id, 0, f"FAILED: {err}")
            return {"t": "ACK"}

        if msg_type == "DATA_PUSH":
            symbol = message.get("symbol")
            equity = self.agent_states.get(client_id, {}).get("equity", 1000.0)
            bid = message.get("bid", 0.0)
            ask = message.get("ask", 0.0)
            tick_val = message.get("tick_val", 10.0)
            tick_size = message.get("tick_size", 0.0001)

            loop = asyncio.get_event_loop()
            analysis_results = await loop.run_in_executor(self.executor, process_analysis, message)
            atr = analysis_results.get("atr", 0.0)

            mgmt_commands = await self.pos_manager.monitor_and_manage(symbol, (bid+ask)/2, atr)

            response = {"t": "DEC", "s": symbol, "act": "WAIT"}
            if mgmt_commands: response["mgmt"] = mgmt_commands
            if "draw" in analysis_results: response["drw"] = analysis_results["draw"]

            if analysis_results.get("action") in ["BUY", "SELL"]:
                action = analysis_results["action"]

                if symbol in self.cooldowns and datetime.datetime.now() < self.cooldowns[symbol]:
                    logger.info(f"Symbol {symbol} in cooldown. Waiting.")
                    return response

                active_trades = await self.ledger.get_active_trades()
                corr_check = self.corr_brain.check_exposure(symbol, action, active_trades)
                if not corr_check["safe"]:
                    logger.info(f"Correlation rejection: {corr_check['reason']}")
                    return response

                price = ask if action == "BUY" else bid
                validation = self.risk_manager.validate_trade(
                    symbol, action, equity,
                    current_price=price, atr=atr, tick_val=tick_val, tick_size=tick_size
                )
                if validation["safe"]:
                    internal_id = await self.ledger.record_intent(
                        symbol, action, validation["lots"],
                        validation["sl"], validation["tp"]
                    )
                    response.update({
                        "id": internal_id, "act": action, "lts": validation["lots"],
                        "sl": validation["sl"], "tp": validation["tp"]
                    })
            return response

        return {"t": "ACK", "m": f"Processed {msg_type}"}

    async def run(self):
        logger.info("Starting Hive Coordinator...")
        await self.ledger.init_db()
        await self.server.start()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
