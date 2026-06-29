import asyncio
import logging
import multiprocessing
import os
import signal
import sys
from typing import Dict, Any, List, Optional
from src.python.hive.ipc import HiveIPC
from src.python.bridge.dashboards.native_gui import NativeDashboard
from src.python.bridge.dashboards.web_server import WebDashboard
from src.python.bridge.watchdog import L99Watchdog

# Strategy Brains
from src.python.brains.strategies.swing_master import SwingMaster
from src.python.brains.strategies.scalp_master import ScalpMaster
from src.python.brains.strategies.vsa_master import VSAMaster
from src.python.brains.strategies.wyckoff_master import WyckoffMaster
from src.python.brains.strategies.ict_killzone import ICTKillzone
from src.python.brains.consensus import MetaBrain

logger = logging.getLogger("AAT_Supervisor")

class HiveOrchestrator:
    """
    10001: The Supervisor (Process 0).
    Responsible for the 23-brain process lifecycle and dynamic affinity mapping.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ipc = HiveIPC()
        self.brains: List[multiprocessing.Process] = []
        self.watchdog = L99Watchdog(self)
        self.running = True

    async def start(self):
        """10002: Orchestration Entry Point."""
        logger.info("Initializing Phoenix Gauntlet V3.3.0...")

        # 1. Reset shared memory
        self.ipc.clear_memory()

        # 2. Start Dashboards
        self._start_dashboards()

        # 3. Start Brains
        self._spawn_brain_swarm()

        # 4. Start Watchdog
        asyncio.create_task(self.watchdog.run())

        logger.info("AAT V3.3.0 Fully Operational.")

        while self.running:
            await asyncio.sleep(1)

    def _start_dashboards(self):
        # Native GUI (Dear PyGui)
        self.native_gui = NativeDashboard()
        # Web Interface (FastAPI)
        self.web_ui = WebDashboard()

    def _spawn_brain_swarm(self):
        """10015: Parallel process spawning with affinity locking."""
        strategy_classes = [
            (SwingMaster, "SwingMaster"),
            (ScalpMaster, "ScalpMaster"),
            (VSAMaster, "VSAMaster"),
            (WyckoffMaster, "WyckoffMaster"),
            (ICTKillzone, "ICTKillzone"),
            (MetaBrain, "MetaBrain")
        ]

        for i, (brain_cls, name) in enumerate(strategy_classes):
            # Dynamic affinity: Skip core 0 (Supervisor) and 1 (Orchestrator)
            cpu_cores = [i + 2]
            brain = brain_cls(name=name, ipc=self.ipc)
            brain.cpu_affinity = cpu_cores

            # Since BaseBrain inherits from Process, we can just call start()
            brain.start()
            self.brains.append(brain)

    async def broadcast_command(self, cmd: Dict[str, Any]):
        """Publish command to all connected clients."""
        self.ipc.xadd("commands", cmd)

    def stop(self, *args):
        self.running = False
        for p in self.brains:
            if p.is_alive():
                p.terminate()
        logger.info("AAT V3.3.0 Shutdown Complete.")
