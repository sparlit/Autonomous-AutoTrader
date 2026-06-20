import pandas as pd
import logging
from typing import Dict, Any, List
from src.python.brains.consensus import ConsensusEngine

logger = logging.getLogger("AAT_Worker")

class StrategyWorker:
    def __init__(self):
        """Magic: 12001"""
        self.engine = ConsensusEngine()
        self.buffers: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.max_history = 1100

    def update_and_analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Magic: 12002"""
        symbol = data.get("s")
        if not symbol: return {"act": "WAIT", "reason": "No symbol", "m_id": 1202}

        if symbol not in self.buffers or "ltf" not in data:
            self.buffers[symbol] = {
                "ltf": data.get("ltf", []),
                "h1": data.get("h1", []),
                "h4": data.get("h4", [])
            }
        else:
            if "h" in data:
                self.buffers[symbol]["ltf"].extend(data["h"])
                self.buffers[symbol]["ltf"] = self.buffers[symbol]["ltf"][-self.max_history:]
            else:
                self.buffers[symbol] = {
                    "ltf": data.get("ltf", []),
                    "h1": data.get("h1", []),
                    "h4": data.get("h4", [])
                }

        analysis_data = {
            "history": self.buffers[symbol]["ltf"],
            "h1": self.buffers[symbol]["h1"],
            "h4": self.buffers[symbol]["h4"],
            "s": symbol,
            "tf": data.get("tf", 0)
        }

        return self.engine.analyze_sync(analysis_data)

_worker = None

def worker_init():
    """Magic: 12003"""
    global _worker
    _worker = StrategyWorker()

def process_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """Magic: 12004"""
    global _worker
    if _worker is None: worker_init()
    try:
        return _worker.update_and_analyze(data)
    except Exception as e:
        logger.error(f"Worker Task Fatal: {e}")
        return {"act": "WAIT", "status": "ERROR", "error": str(e), "m_id": 1204}
