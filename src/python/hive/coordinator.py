import asyncio
import logging
import ujson as json
from typing import Dict, Any, List
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.base import BrainRegistry
from src.python.execution.risk_manager import RiskManager
from src.python.execution.ledger import TradeLedger

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
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self._initialize_brains()

    def _initialize_brains(self):
        from src.python.brains.specialized import (
            HTFAnalysisBrain, LTFTriggerBrain, CorrelationBrain, DecisionBrain
        )
        self.registry.register(HTFAnalysisBrain("HTF_Analyst"))
        self.registry.register(LTFTriggerBrain("LTF_Trigger"))
        self.registry.register(CorrelationBrain("Correlation_Analyst"))
        self.registry.register(DecisionBrain("Decision_Maker"))

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "PNG": return {"type": "PING"}
        if m_type == "HB":
            return {"type": "HEARTBEAT", "symbol": message.get("s"), "equity": message.get("e"), "drawdown": message.get("d")}
        if m_type == "DP":
            raw_h = message.get("h", [])
            history = [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4]} for x in raw_h]
            return {"type": "DATA_PUSH", "symbol": message.get("s"), "tf": message.get("tf"), "history": history, "bid": message.get("bi"), "ask": message.get("as")}
        if m_type == "T_ACK":
            return {"type": "TRADE_ACK", "id": message.get("id"), "ticket": message.get("tk"), "err": message.get("err")}
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

        if msg_type == "TRADE_ACK":
            internal_id = message.get("id")
            ticket = message.get("ticket")
            err = message.get("err")
            if ticket and ticket > 0:
                self.ledger.update_execution(internal_id, ticket, "OPEN")
                logger.info(f"Trade confirmed on MT5. Ticket: {ticket}")
            else:
                self.ledger.update_execution(internal_id, 0, f"FAILED: {err}")
                logger.error(f"Trade failed on MT5: {err}")
            return {"t": "ACK"}

        if msg_type == "DATA_PUSH":
            symbol = message.get("symbol")
            equity = self.agent_states.get(client_id, {}).get("equity", 1000.0)
            bid = message.get("bid", 0.0)
            ask = message.get("ask", 0.0)

            results = await self.registry.process_all(message)
            decision_maker = results.get("Decision_Maker", {})
            atr = decision_maker.get("atr", 0.0)

            response = {"t": "DEC", "s": symbol, "act": "WAIT"}
            if "draw" in decision_maker: response["drw"] = decision_maker["draw"]

            if decision_maker.get("action") in ["BUY", "SELL"]:
                price = ask if decision_maker["action"] == "BUY" else bid
                validation = self.risk_manager.validate_trade(symbol, decision_maker["action"], equity, current_price=price, atr=atr)
                if validation["safe"]:
                    internal_id = self.ledger.record_intent(
                        symbol, validation["action"], validation["lots"],
                        validation["sl"], validation["tp"]
                    )
                    response.update({
                        "id": internal_id,
                        "act": validation["action"],
                        "lts": validation["lots"],
                        "sl": validation["sl"],
                        "tp": validation["tp"]
                    })
                else:
                    logger.info(f"Trade rejected: {validation['reason']}")

            return response

        return {"t": "ACK", "m": f"Processed {msg_type}"}

    async def run(self):
        logger.info("Starting Hive Coordinator...")
        await self.server.start()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
