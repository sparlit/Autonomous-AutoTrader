import multiprocessing
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_IPC")

class HiveIPC:
    """10250: True IPC layer using standard multiprocessing primitives.
    Hardened for Windows 'spawn' compatibility."""
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self._queues: Dict[str, multiprocessing.Queue] = self.manager.dict()
        self._shared_state = self.manager.dict()
        self._lock = self.manager.Lock()

    def __getstate__(self):
        """Prepare state for pickling (Windows compatibility)."""
        state = self.__dict__.copy()
        # Remove the manager and lock as they cannot be pickled
        # The proxy objects (_queues, _shared_state) are picklable.
        del state['manager']
        del state['_lock']
        return state

    def __setstate__(self, state):
        """Restore state after pickling."""
        self.__dict__.update(state)
        self.manager = None # Not available in child
        self._lock = None   # Not available in child

    def get_queue(self, name: str) -> multiprocessing.Queue:
        # Avoid creating excessive queues if not needed
        if name not in self._queues:
            if self._lock is None:
                # In child process, we cannot create new queues if they don't exist
                # because we don't have the manager/lock.
                # This requires the parent to pre-initialize all queues.
                raise RuntimeError(f"Queue '{name}' not found in child process and cannot be created dynamically on Windows.")

            with self._lock:
                if name not in self._queues:
                    self._queues[name] = self.manager.Queue(maxsize=1000)
        return self._queues[name]

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        """Emulate Redis XADD."""
        try:
            q = self.get_queue(stream)
            if q.full():
                try:
                    q.get_nowait()
                except Exception:
                    # Queue might have been cleared by another process
                    logger.debug("Failed to get_nowait from full queue")
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
            except Exception:
                # Log or ignore error during read
                logger.debug(f"XREAD failed for {stream_name}")
        return results

    def xdel(self, stream: str, msg_id: str):
        """10251: Delete message (placeholder for Redis compatibility)."""
        return True

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
