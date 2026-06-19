import asyncio
import logging
import ujson as json
from typing import Dict, Any, List
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.base import BrainRegistry
from src.python.execution.risk_manager import RiskManager

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

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")

        if msg_type == "PING":
            return {"type": "PONG"}

        if msg_type == "HEARTBEAT":
            symbol = message.get("symbol", "UNKNOWN")
            self.agent_states[client_id] = {
                "symbol": symbol,
                "last_seen": asyncio.get_event_loop().time(),
                "status": "HEALTHY",
                "equity": float(message.get("equity", 0.0)),
                "drawdown": float(message.get("drawdown", 0.0))
            }
            return {"type": "HEARTBEAT_ACK"}

        if msg_type == "DATA_PUSH":
            symbol = message.get("symbol")
            equity = self.agent_states.get(client_id, {}).get("equity", 1000.0)

            results = await self.registry.process_all(message)
            decision_maker = results.get("Decision_Maker", {})

            response = {"type": "DECISION", "symbol": symbol, "action": "WAIT"}

            if "draw" in decision_maker:
                response["draw"] = decision_maker["draw"]

            if decision_maker.get("action") in ["BUY", "SELL"]:
                validation = self.risk_manager.validate_trade(symbol, decision_maker["action"], equity)
                if validation["safe"]:
                    response["action"] = validation["action"]
                    response["lots"] = validation["lots"]
                else:
                    logger.info(f"Trade rejected: {validation['reason']}")

            return response

        return {"type": "ACK", "msg": f"Processed {msg_type}"}

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
