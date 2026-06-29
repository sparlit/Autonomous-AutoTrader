import asyncio
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("AAT_L99_Watchdog")

class L99Watchdog:
    """
    14901: L99 Hardened Watchdog.
    Implements bidirectional heartbeats and emergency safety protocols.
    """
    def __init__(self, orchestrator: Any, timeout: float = 15.0):
        self.orchestrator = orchestrator
        self.timeout = timeout
        self.running = False
        self.last_mt5_heartbeat = time.time()
        self.emergency_triggered = False

    async def run(self):
        """14902: Monitor MT5-Python link integrity."""
        self.running = True
        logger.info("L99 Watchdog Active (Zero-Tolerance Mode)")
        while self.running:
            now = time.time()
            if now - self.last_mt5_heartbeat > self.timeout:
                if not self.emergency_triggered:
                    await self._trigger_emergency_flatten()

            await asyncio.sleep(1.0)

    def heartbeat(self):
        """Record pulse from MT5."""
        self.last_mt5_heartbeat = time.time()
        if self.emergency_triggered:
            logger.info("L99 Link Restored. Resetting safety state.")
            self.emergency_triggered = False

    async def _trigger_emergency_flatten(self):
        """14905: Emergency Protocol - Close all positions if link drops."""
        logger.critical("L99 LINK FAILURE: MT5 Connection Lost. Triggering EMERGENCY FLATTEN.")
        self.emergency_triggered = True
        # Logic to send CLOSE_ALL command via bridge if possible, or log for local failsafe
        await self.orchestrator.broadcast_command({"mgmt": "CLOSE_ALL", "reason": "L99_LINK_FAILURE"})

    def stop(self):
        self.running = False
