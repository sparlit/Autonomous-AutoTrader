import asyncio
import logging
from typing import Dict, Any, List
from src.python.bridge.server import BridgeServer
from src.python.hive.config import load_config
from src.python.brains.registry import BrainRegistry
from src.python.brains.sequential_brain import SequentialBrain
from src.python.brains.consensus_brain import ConsensusBrain

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

        # Initialize Brains
        self.registry = BrainRegistry()
        self.registry.load_strategies()

        all_strats = list(self.registry.strategies.values())
        self.sequential_brain = SequentialBrain(all_strats[:2]) # First 2 as Stage 1
        self.consensus_brain = ConsensusBrain(
            all_strats,
            threshold=self.config.brains.consensus_threshold
        )

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")

        if msg_type == "PING":
            return {"type": "PONG"}

        if msg_type == "HEARTBEAT":
            symbol = message.get("symbol", "UNKNOWN")
            self.agent_states[client_id] = {
                "symbol": symbol,
                "last_seen": asyncio.get_event_loop().time(),
                "status": "HEALTHY"
            }
            return {"type": "HEARTBEAT_ACK"}

        if msg_type == "OHLC_PUSH":
            # 3-Stage Pipeline Execution
            # Stage 1: Sequential
            signal = await self.sequential_brain.process(message)

            # Stage 2: Consensus (if Stage 1 is Neutral)
            if not signal:
                signal = await self.consensus_brain.process(message)

            if signal:
                logger.info(f"SIGNAL GENERATED: {signal.symbol} | Dir: {signal.direction} | Conf: {signal.confidence}")
                return {
                    "type": "SIGNAL",
                    "direction": signal.direction,
                    "confidence": signal.confidence,
                    "strategy": signal.strategy_name
                }

            return {"type": "ACK", "status": "NEUTRAL"}

        return {"type": "ERROR", "msg": f"Unknown message type: {msg_type}"}

    async def run(self):
        logger.info("Starting Hive Coordinator...")
        await self.server.start()

if __name__ == "__main__":
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
