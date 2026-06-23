import multiprocessing
import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_IPC")

class HiveIPC:
    """10250: True IPC layer using standard multiprocessing primitives.
    Hardened for Windows 'spawn' compatibility."""
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self._queues = self.manager.dict()
        self._shared_state = self.manager.dict()
        self._lock = self.manager.Lock()

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['manager']
        del state['_lock']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.manager = None
        self._lock = None

    def get_queue(self, name: str) -> multiprocessing.Queue:
        if name not in self._queues:
            if self._lock is None:
                raise RuntimeError(f"Queue '{name}' not found in child process. Parent must pre-initialize.")

            with self._lock:
                if name not in self._queues:
                    self._queues[name] = self.manager.Queue(maxsize=1000)
        return self._queues[name]

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        try:
            q = self.get_queue(stream)
            if q.full():
                try: q.get_nowait()
                except Exception: logger.debug("IPC queue pop failed")
            q.put_nowait(data)
        except Exception as e:
            logger.error(f"IPC XADD Fail on {stream}: {e}")

    def xread(self, streams: Dict[str, str], count: int = 1, block: int = 0) -> List[Any]:
        results = []
        for stream_name in streams.keys():
            try:
                q = self.get_queue(stream_name)
                msgs = []
                for _ in range(count):
                    if q.empty(): break
                    msgs.append(("msg_id", {b'payload': q.get_nowait().get("payload")}))
                if msgs:
                    results.append((stream_name, msgs))
            except Exception: logger.debug("IPC xread transient fail")
        return results

    def xdel(self, stream: str, msg_id: str):
        return True

    def set_state(self, key: str, value: Any):
        # Retry loop for Windows manager proxy access
        for i in range(3):
            try:
                self._shared_state[key] = value
                return
            except Exception as e:
                if i == 2: logger.error(f"IPC State Set Fail after 3 attempts: {e}")
                time.sleep(0.01)

    def get_state(self, key: str, default: Any = None) -> Any:
        for i in range(3):
            try:
                return self._shared_state.get(key, default)
            except Exception:
                if i == 2: return default
                time.sleep(0.01)

    def get_all_state(self) -> Dict[str, Any]:
        try:
            return dict(self._shared_state)
        except Exception:
            return {}

_ipc_instance = None

def get_ipc() -> HiveIPC:
    global _ipc_instance
    if _ipc_instance is None:
        _ipc_instance = HiveIPC()
    return _ipc_instance
