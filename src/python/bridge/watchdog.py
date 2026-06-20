import asyncio
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("AAT_Watchdog")

class SystemWatchdog:
    def __init__(self, agent_states: Dict[str, Dict[str, Any]], timeout: float = 30.0):
        """
        Initialize the SystemWatchdog with agent state tracking and timeout thresholds.
        """
        self.agent_states = agent_states
        self.timeout = timeout
        self.latencies: Dict[str, float] = {}

    async def run(self):
        """
        Periodically monitor all registered agents for health and inactivity.
        """
        logger.info("Watchdog started.")
        while True:
            await asyncio.sleep(5)
            now = time.time()
            for client_id, state in list(self.agent_states.items()):
                last_seen = state.get("last_seen", 0)
                symbol = state.get("symbol", "UNKNOWN")

                if now - last_seen > self.timeout:
                    logger.warning(f"CRITICAL: Agent {client_id} ({symbol}) TIMEOUT! Dead for {now - last_seen:.1f}s")
                    self.agent_states.pop(client_id, None)
                else:
                    # Log health metrics for observability
                    logger.debug(f"Agent {client_id} status: OK. Last seen: {now - last_seen:.1f}s ago.")

    def record_rtt(self, client_id: str, client_sent_time: float):
        """Record round-trip time for latency monitoring."""
        if client_sent_time > 0:
            rtt = time.time() - client_sent_time
            self.latencies[client_id] = rtt
            if rtt > 0.5: # 500ms threshold
                logger.warning(f"High Latency for {client_id}: {rtt*1000:.1f}ms")
