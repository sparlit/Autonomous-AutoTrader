# Version: V3.1.0-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
import logging
import time
import os
from typing import Dict, Any, List

from shared.memory import SharedState, MessageQueue
from shared.config_manager import load_aat_config
from gateways.python_bridge import InstitutionalBridge
from logic.base_brain import SMCBrain, VSABrain
from logic.meta_consensus import MetaConsensusBrain
from execution.risk_engine import InstitutionalRiskEngine
from ui.kanban_dashboard import KanbanDashboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AAT_Core - %(levelname)s - %(message)s')
logger = logging.getLogger("AAT_Orchestrator")

class PhoenixOrchestrator:
    """10100: Master lifecycle manager and message router."""
    def __init__(self):
        self.config = load_aat_config()
        self.shm = SharedState()

        # Message Queues
        self.brain_in_q = MessageQueue("brains_in")
        self.brain_out_q = MessageQueue("brains_out")

        # Bridge
        self.bridge = InstitutionalBridge(
            self.config.bridge.host,
            self.config.bridge.port,
            self.shm,
            self.brain_in_q
        )

        # Risk
        self.risk = InstitutionalRiskEngine(self.config.risk, self.shm)

        # Brains
        self.brains = [
            SMCBrain("SMC_1", self.shm, self.brain_in_q, self.brain_out_q),
            VSABrain("VSA_1", self.shm, self.brain_in_q, self.brain_out_q),
            MetaConsensusBrain("Meta_1", self.shm, self.brain_out_q, self.brain_out_q)
        ]

        # Dashboard
        self.dash = KanbanDashboard(self.shm)

    async def run(self):
        logger.info("🌌 Launching Phoenix Ascendant Orchestrator...")

        # Start Dashboard
        self.dash.start()

        # Start Brains
        for brain in self.brains:
            brain.start()

        # Start Bridge Task
        asyncio.create_task(self.bridge.start())

        # Main Processing Loop
        await self._orchestration_loop()

    async def _orchestration_loop(self):
        logger.info("Orchestration Loop Active.")
        while True:
            # Drain brain outputs
            results = self.brain_out_q.pop_all()
            for res in results:
                if res.get('type') == 'EXECUTION':
                    if self.risk.validate_execution(res):
                        order = {
                            "t": "ORD",
                            "s": res['symbol'],
                            "act": res['act'],
                            "v": self.risk.calculate_lots(res['symbol'])
                        }
                        logger.info(f"🚀 ORDER DISPATCHED: {order}")
                        await self.bridge.broadcast(order)

            await asyncio.sleep(0.01)

    def stop(self):
        self.dash.terminate()
        for brain in self.brains:
            brain.terminate()
        self.shm.cleanup()
        self.brain_in_q.cleanup()
        self.brain_out_q.cleanup()
