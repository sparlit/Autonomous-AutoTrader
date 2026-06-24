import multiprocessing
import logging
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
        self._local_cache = {}

    def __getstate__(self):
        """Prepare state for pickling (Windows compatibility)."""
        state = self.__dict__.copy()
        # The proxy objects (_queues, _shared_state) are picklable.
        # We exclude the manager and lock as they cannot be pickled directly.
        del state['manager']
        del state['_lock']
        # Local cache is not picklable if it contains non-picklable proxies from different managers
        # but here they are from the same manager. However, it's safer to clear it.
        state['_local_cache'] = {}
        return state

    def __setstate__(self, state):
        """Restore state after pickling."""
        self.__dict__.update(state)
        self.manager = None
        self._lock = None
        if not hasattr(self, '_local_cache'):
            self._local_cache = {}

    def get_queue(self, name: str) -> multiprocessing.Queue:
        if name in self._local_cache:
            return self._local_cache[name]

        if name not in self._queues:
            if self._lock is None:
                # In child process, we cannot create new queues if they don't exist
                raise RuntimeError(f"Queue '{name}' not found in child process. Parent must pre-initialize.")

            with self._lock:
                if name not in self._queues:
                    self._queues[name] = self.manager.Queue(maxsize=1000)

        q = self._queues[name]
        self._local_cache[name] = q
        return q

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        """Emulate Redis XADD."""
        try:
            q = self.get_queue(stream)
            if q.full():
                try: q.get_nowait()
                except Exception: logger.debug("IPC cleanup")
            q.put_nowait(data)
        except Exception as e:
            logger.error(f"IPC XADD Fail on {stream}: {e}")

    def xread(self, streams: Dict[str, str], count: int = 1, block: int = 0) -> List[Any]:
        """Emulate Redis XREAD."""
        results = []
        for stream_name in streams.keys():
            try:
                q = self.get_queue(stream_name)
                msgs = []
                for _ in range(count):
                    if q.empty():
                        break
                    msgs.append(("msg_id", {b'payload': q.get_nowait().get("payload")}))
                if msgs:
                    results.append((stream_name, msgs))
            except Exception: logger.debug("IPC cleanup")
        return results

    def xdel(self, stream: str, msg_id: str):
        return True

    def set_state(self, key: str, value: Any):
        """Thread-safe state update."""
        try:
            self._shared_state[key] = value
        except Exception as e:
            logger.error(f"IPC State Set Fail: {e}")

    def get_state(self, key: str, default: Any = None) -> Any:
        """Thread-safe state retrieval."""
        try:
            return self._shared_state.get(key, default)
        except Exception:
            return default

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
