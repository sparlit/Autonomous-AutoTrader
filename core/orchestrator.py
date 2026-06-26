# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
import logging
import time
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
        self.shm = SharedState(size=self.config.system.shm_size_mb * 1024 * 1024)
        self.control_shm = SharedState(name="aat_control_state", size=1024 * 100) # 100KB for control

        # Initialize Control State
        self.control_shm.set_data({"paused": False, "manual_mode": False})

        # Message Queues
        q_size = self.config.system.queue_size_kb * 1024
        self.brain_in_q = MessageQueue("brains_in", size=q_size)
        self.brain_out_q = MessageQueue("brains_out", size=q_size)

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
        self.brains = []
        if "SMC_1" in self.config.brains.enabled_brains:
            self.brains.append(SMCBrain("SMC_1", self.shm, self.brain_in_q, self.brain_out_q))
        if "VSA_1" in self.config.brains.enabled_brains:
            self.brains.append(VSABrain("VSA_1", self.shm, self.brain_in_q, self.brain_out_q))
        if "Meta_1" in self.config.brains.enabled_brains:
            self.brains.append(MetaConsensusBrain("Meta_1", self.shm, self.brain_out_q, self.brain_out_q, threshold=self.config.brains.consensus_threshold))

        # Dashboard
        self.dash = KanbanDashboard(self.shm, self.control_shm)

    async def run(self):
        logger.info("🌌 Launching Phoenix Ascendant Orchestrator V3.1...")
        self.dash.start()
        for brain in self.brains: brain.start()
        asyncio.create_task(self.bridge.start())
        await self._orchestration_loop()

    async def _orchestration_loop(self):
        logger.info("Orchestration Loop Active.")
        tick = self.config.brains.tick_rate_ms / 1000.0
        while True:
            control = self.control_shm.get_data()
            if not control.get("paused", False):
                results = self.brain_out_q.pop_all()
                for res in results:
                    if res.get('type') == 'EXECUTION':
                        if self.risk.validate_execution(res):
                            order = {
                                "t": "ORD",
                                "s": res['symbol'],
                                "act": res['act'],
                                "v": self.risk.calculate_lots(res['symbol']),
                                "m": self.config.system.global_magic
                            }
                            logger.info(f"🚀 ORDER DISPATCHED: {order}")
                            await self.bridge.broadcast(order)

            await asyncio.sleep(tick)

    def stop(self):
        self.dash.terminate()
        for brain in self.brains: brain.terminate()
        self.shm.cleanup(); self.control_shm.cleanup()
        self.brain_in_q.cleanup(); self.brain_out_q.cleanup()
