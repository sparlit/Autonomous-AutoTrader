import asyncio
import logging
import time
from typing import Dict, Any

logger = logging.getLogger("AAT_Watchdog")

class SystemWatchdog:
    def __init__(self, agent_states: Dict[str, Dict[str, Any]], timeout: float = 30.0):
        """
        Initialize a SystemWatchdog to monitor client staleness.

        Parameters:
		agent_states (Dict[str, Dict[str, Any]]): Shared dictionary mapping client IDs to state dictionaries.
		timeout (float): Staleness threshold in seconds. Defaults to 30.0.
        """
        self.agent_states = agent_states
        self.timeout = timeout
        self.running = False

    async def run(self):
        """
        Periodically check agent states and remove entries for clients exceeding the staleness timeout.

        This method runs indefinitely until stop() is called, continuously monitoring the shared agent_states
        dictionary and removing entries for clients whose last_seen timestamp exceeds the configured timeout.
        """
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
        """
        Stop the watchdog loop.
        """
        self.running = False
