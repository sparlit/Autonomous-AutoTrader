import pandas as pd
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from src.python.brains.consensus import ConsensusEngine

logger = logging.getLogger("AAT_Worker")

class StrategyWorker:
    """A long-lived worker process with internal thread-level parallelism."""
    def __init__(self):
        """
        Initialize a strategy worker capable of consensus-based analysis across multiple symbols.

        Sets up the worker with a consensus engine, per-symbol history buffers, and resources for
        parallel task execution.
        """
        self.engine = ConsensusEngine()
        self.buffers: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.max_history = 1100
        # Internal ThreadPool for parallelizing strategy sub-tasks (SMC, VSA, Indicators)
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

    def update_and_analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the symbol's historical buffers and perform consensus analysis.

        Parameters:
		data (Dict[str, Any]): Market data with symbol identifier under key "s".

        Returns:
		Dict[str, Any]: Analysis result with trading action and context.
        """
        symbol = data.get("s")
        if not symbol: return {"action": "WAIT", "reason": "No symbol"}

        if symbol not in self.buffers:
            self.buffers[symbol] = {
                "ltf": data.get("ltf", []),
                "h1": data.get("h1", []),
                "h4": data.get("h4", [])
            }
        else:
            if "h" in data: # Incremental
                self.buffers[symbol]["ltf"].extend(data["h"])
                self.buffers[symbol]["ltf"] = self.buffers[symbol]["ltf"][-self.max_history:]
            else: # Full
                self.buffers[symbol] = {
                    "ltf": data.get("ltf", []),
                    "h1": data.get("h1", []),
                    "h4": data.get("h4", [])
                }

        # Analyze using ThreadPool for sub-tasks
        analysis_data = {
            "history": self.buffers[symbol]["ltf"],
            "h1": self.buffers[symbol]["h1"],
            "h4": self.buffers[symbol]["h4"]
        }

        # We can't easily thread individual methods of ConsensusEngine without refactoring it,
        # but we can call the entire analyze_sync in the pool if we have multiple symbols per worker.
        # For now, analyze_sync is optimized via vectorization.
        return self.engine.analyze_sync(analysis_data)

_worker = None

def worker_init():
    """
    Initialize the module-level worker instance.
    """
    global _worker
    _worker = StrategyWorker()

def process_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a data task through the consensus worker.

    Parameters:
	data (Dict[str, Any]): Market data including symbol and timeframe histories

    Returns:
	Dict[str, Any]: An action dictionary containing the analysis result or error response
    """
    global _worker
    if _worker is None: worker_init()
    try:
        return _worker.update_and_analyze(data)
    except Exception as e:
        logger.error(f"Worker Task Error: {e}")
        return {"action": "WAIT", "error": str(e)}
