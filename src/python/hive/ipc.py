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

    def clear_memory(self):
        """10251: Wipe all shared state and queues for a fresh startup."""
        logger.info("🧹 Clearing IPC memory state...")
        with self._lock:
            self._shared_state.clear()
            # Note: We don't necessarily want to delete the queues themselves as they might be mapped,
            # but we should clear their contents.
            for name in self._queues.keys():
                q = self._queues[name]
                while not q.empty():
                    try: q.get_nowait()
                    except: break
        logger.info("✅ IPC memory cleared.")

    def __getstate__(self):
        """Prepare state for pickling (Windows compatibility)."""
        state = self.__dict__.copy()
        del state['manager']
        del state['_lock']
        state['_local_cache'] = {}
        return state

    def __setstate__(self, state):
        """Restore state after pickling."""
        self.__dict__.update(state)
        self.manager = None
        self._lock = None
        if not hasattr(self, '_local_cache'):
            self._local_cache = {}

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
        # Avoid creating excessive queues if not needed
        if name not in self._queues:
            if self._lock is None:
                raise RuntimeError(f"Queue '{name}' not found in child process. Parent must pre-initialize.")

            with self._lock:
                if name not in self._queues:
                    self._queues[name] = self.manager.Queue(maxsize=1000)

        q = self._queues[name]
        self._local_cache[name] = q
        return q

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        """Emulate Redis XADD."""
        q = self.get_queue(stream)
        try:
            q = self.get_queue(stream)
            if q.full():
                try: q.get_nowait()
                except: pass
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
                    if q.empty():
                        break
                    msgs.append(("msg_id", {b'payload': q.get_nowait().get("payload")}))
                if msgs:
                    results.append((stream_name, msgs))
            except Exception as e:
                pass
        return results

    def xdel(self, stream: str, msg_id: str):
        return True

    def set_state(self, key: str, value: Any):
        self._shared_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._shared_state.get(key, default)

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
