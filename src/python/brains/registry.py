import logging
from typing import Dict, Any, List
from multiprocessing import Queue
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_BrainRegistry")

class BrainRegistry:
    """12004: Process registry and supervisor."""
    def __init__(self):
        """Initialize an empty brain registry."""
        self._brains: Dict[str, BaseBrain] = {}

    def register(self, brain: BaseBrain):
        """Register a brain instance."""
        self._brains[brain.name] = brain
        logger.info(f"Brain registered: {brain.name}")

    def start_all(self):
        """Launch all registered brain processes."""
        for name, brain in self._brains.items():
            if not brain.is_alive():
                logger.info(f"Starting brain process: {name}")
                brain.start()

    def stop_all(self):
        """Gracefully stop all brain processes."""
        for name, brain in self._brains.items():
            if brain.is_alive():
                logger.info(f"Stopping brain process: {name}")
                brain.terminate()
                brain.join(timeout=2)

    def get_health_report(self) -> List[Dict[str, Any]]:
        """Collect health metrics from all brains."""
        # Note: In a real multi-process environment, health stats should be pushed to a shared state
        # or collected via IPC. For simplicity here, we assume the Orchestrator tracks this.
        return [brain.health() for brain in self._brains.values()]

