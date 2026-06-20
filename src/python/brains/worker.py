import pandas as pd
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from src.python.brains.consensus import ConsensusEngine

logger = logging.getLogger("AAT_Worker")

class StrategyWorker:
    """A long-lived worker process with internal thread-level parallelism."""
    def __init__(self):
        self.engine = ConsensusEngine()
        self.buffers: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.max_history = 1100
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

    def update_and_analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = data.get("s")
        if not symbol: return {"act": "WAIT", "reason": "No symbol"}

        # Handle fragmented packets and full vs incremental pushes
        # Tier 4.1: Persistence across worker restarts
        # The coordinator now sends full history if buffer is missing
        if symbol not in self.buffers or "ltf" not in data:
            self.buffers[symbol] = {
                "ltf": data.get("ltf", []),
                "h1": data.get("h1", []),
                "h4": data.get("h4", [])
            }
        else:
            # Incremental Update (if provided in protocol extension)
            if "h" in data:
                self.buffers[symbol]["ltf"].extend(data["h"])
                self.buffers[symbol]["ltf"] = self.buffers[symbol]["ltf"][-self.max_history:]
            else:
                # Fallback to full overwrite from message
                self.buffers[symbol] = {
                    "ltf": data.get("ltf", []),
                    "h1": data.get("h1", []),
                    "h4": data.get("h4", [])
                }

        analysis_data = {
            "history": self.buffers[symbol]["ltf"],
            "h1": self.buffers[symbol]["h1"],
            "h4": self.buffers[symbol]["h4"]
        }

        return self.engine.analyze_sync(analysis_data)

_worker = None

def worker_init():
    global _worker
    _worker = StrategyWorker()

def process_task(data: Dict[str, Any]) -> Dict[str, Any]:
    global _worker
    if _worker is None: worker_init()
    try:
        return _worker.update_and_analyze(data)
    except Exception as e:
        logger.error(f"Worker Task Error: {e}")
        return {"act": "WAIT", "error": str(e)}
