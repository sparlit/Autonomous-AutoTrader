import multiprocessing
import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_IPC")

class HiveIPC:
    """10250: True IPC layer using standard multiprocessing primitives."""
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self._queues: Dict[str, multiprocessing.Queue] = self.manager.dict()
        self._shared_state = self.manager.dict()
        self._lock = self.manager.Lock()

    def get_queue(self, name: str) -> multiprocessing.Queue:
        # Avoid creating excessive queues if not needed
        if name not in self._queues:
            with self._lock:
                if name not in self._queues:
                    self._queues[name] = self.manager.Queue(maxsize=1000)
        return self._queues[name]

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        """Emulate Redis XADD."""
        q = self.get_queue(stream)
        try:
            if q.full():
                try: q.get_nowait()
                except: pass
            q.put_nowait(data)
        except Exception as e:
            logger.error(f"IPC XADD Fail on {stream}: {e}")

    def xread(self, streams: Dict[str, str], count: int = 1, block: int = 0) -> List[Any]:
        """Emulate Redis XREAD."""
        results = []
        for stream_name in streams.keys():
            q = self.get_queue(stream_name)
            msgs = []
            try:
                for _ in range(count):
                    if q.empty(): break
                    msgs.append(("msg_id", {b'payload': q.get_nowait().get("payload")}))
                if msgs:
                    results.append((stream_name, msgs))
            except Exception as e:
                pass
        return results

    def xdel(self, stream: str, msg_id: str):
        pass

    def set_state(self, key: str, value: Any):
        self._shared_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._shared_state.get(key, default)

    def get_all_state(self) -> Dict[str, Any]:
        # Return a static copy to avoid proxy issues in loops
        return dict(self._shared_state)

_ipc_instance = None

def get_ipc() -> HiveIPC:
    global _ipc_instance
    if _ipc_instance is None:
        _ipc_instance = HiveIPC()
    return _ipc_instance
