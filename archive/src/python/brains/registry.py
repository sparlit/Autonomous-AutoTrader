import logging
from typing import Dict, Any, List
from src.python.brains.base import BaseBrain
from src.python.hive.ipc import get_ipc

logger = logging.getLogger("AAT_BrainRegistry")

class BrainRegistry:
    """12004: Process registry and supervisor."""
    def __init__(self):
        """Initialize an empty brain registry."""
        self._brains: Dict[str, BaseBrain] = {}
        self.ipc = get_ipc()

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
        """Collect health metrics from all brains via IPC shared state."""
        reports = []
        for name in self._brains.keys():
            report = self.ipc.get_state(f"brain_health:{name}")
            if report:
                reports.append(report)
            else:
                # Fallback if no report yet
                reports.append({"name": name, "status": "STARTING"})
        return reports
