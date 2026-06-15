import asyncio
import logging
from typing import Dict, Any
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_Coordinator")

class HiveCoordinator:
    def __init__(self):
        self.config = load_config()
        self.server = BridgeServer(
            self.config.bridge.host,
            self.config.bridge.port,
            self.handle_message
        )
        self.agent_states: Dict[str, Dict[str, Any]] = {}

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")

        if msg_type == "PING":
            return {"type": "PONG"}

        if msg_type == "HEARTBEAT":
            # Update agent state/health
            symbol = message.get("symbol", "UNKNOWN")
            self.agent_states[client_id] = {
                "symbol": symbol,
                "last_seen": asyncio.get_event_loop().time(),
                "status": "HEALTHY"
            }
            return {"type": "HEARTBEAT_ACK"}

        # Dispatch to specific brains based on message type
        # For Week 1, we just log and return a basic ACK
        logger.info(f"Received {msg_type} from {client_id}: {message}")
        return {"type": "ACK", "msg": f"Processed {msg_type}"}

    async def run(self):
        logger.info("Starting Hive Coordinator...")
        await self.server.start()

if __name__ == "__main__":
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
