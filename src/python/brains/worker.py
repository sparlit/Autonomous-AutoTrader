import pandas as pd
from typing import Dict, Any, List
from src.python.brains.consensus import ConsensusEngine

class StrategyWorker:
    """A long-lived worker process that maintains state for multiple symbols."""
    def __init__(self):
        self.engine = ConsensusEngine()
        self.buffers: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.max_history = 1100

    def update_and_analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = data.get("s")
        if not symbol: return {"action": "WAIT", "reason": "No symbol"}

        # Initialize or Update Buffers
        if symbol not in self.buffers:
            self.buffers[symbol] = {
                "ltf": data.get("ltf", []),
                "h1": data.get("h1", []),
                "h4": data.get("h4", [])
            }
        else:
            # Incremental Update if only partial data is sent (optimization)
            if "h" in data: # Single candle push
                self.buffers[symbol]["ltf"].extend(data["h"])
                self.buffers[symbol]["ltf"] = self.buffers[symbol]["ltf"][-self.max_history:]
            else: # Full refresh
                self.buffers[symbol] = {
                    "ltf": data.get("ltf", []),
                    "h1": data.get("h1", []),
                    "h4": data.get("h4", [])
                }

        # Run Analysis using the resident state
        analysis_data = {
            "history": self.buffers[symbol]["ltf"],
            "h1": self.buffers[symbol]["h1"],
            "h4": self.buffers[symbol]["h4"]
        }

        return self.engine.analyze_sync(analysis_data)

# Global worker instance for the process
_worker = None

def worker_init():
    global _worker
    _worker = StrategyWorker()

def process_task(data: Dict[str, Any]) -> Dict[str, Any]:
    global _worker
    if _worker is None: worker_init()
    return _worker.update_and_analyze(data)
