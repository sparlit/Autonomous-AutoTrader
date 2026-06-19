import asyncio
import logging
import time
from typing import Dict, Any

logger = logging.getLogger("AAT_Watchdog")

class SystemWatchdog:
    def __init__(self, agent_states: Dict[str, Dict[str, Any]], timeout: float = 30.0):
        self.agent_states = agent_states
        self.timeout = timeout
        self.running = False

    async def run(self):
        self.running = True
        logger.info("Watchdog started.")
        while self.running:
            now = time.time()
            stale_clients = []
            for client_id, state in self.agent_states.items():
                if now - state.get("last_seen", 0) > self.timeout:
                    logger.warning(f"Client {client_id} ({state.get('symbol')}) is STALE.")
                    stale_clients.append(client_id)

            # Clean up stale states (Coordinator will handle actual socket closure via Server)
            for cid in stale_clients:
                self.agent_states.pop(cid, None)

            await asyncio.sleep(10.0) # Check every 10s

    def stop(self):
        self.running = False
