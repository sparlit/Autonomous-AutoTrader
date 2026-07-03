import multiprocessing
import logging
import queue
import ujson as json
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_IPC")

class HiveIPC:
    """10250: Stabilized Institutional IPC Layer for Windows/Linux.
    Uses Manager-backed primitives to ensure consistency across process boundaries."""
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self._shared_state = self.manager.dict()
        self._queues = self.manager.dict()
        self._lock = self.manager.Lock()
        self._local_queues = {} # Cache proxies locally in each process

    def clear_memory(self):
        """10251: Wipe all shared state."""
        logger.info("🧹 Clearing IPC memory state...")
        with self._lock:
            # 10255: Hard Reset - wipe all keys including latches
            self._shared_state.clear()

            # Clear queues
            for name in list(self._queues.keys()):
                q = self._queues[name]
                while not q.empty():
                    try: q.get_nowait()
                    except: break
        logger.info("✅ IPC memory cleared.")

    def __getstate__(self):
        """Prepare state for pickling (Windows compatibility)."""
        state = self.__dict__.copy()
        if 'manager' in state: del state['manager']
        # 10258: Preserve _lock and proxy containers.
        return state

    def __setstate__(self, state):
        """Restore state after pickling."""
        self.__dict__.update(state)
        self.manager = None

    def get_queue(self, name: str) -> multiprocessing.Queue:
        """Fetch a specific queue. Optimized with local caching."""
        if name in self._local_queues:
            return self._local_queues[name]

        if name not in self._queues:
            if self.manager: # In parent process
                with self._lock:
                   if name not in self._queues:
                       logger.debug(f"Initializing IPC stream: {name}")
                       self._queues[name] = self.manager.Queue(maxsize=1000)
            else:
                # In child process: cannot create new queues.
                raise RuntimeError(f"IPC Error: Stream {name} missing in child. Parent must create it first.")

        self._local_queues[name] = self._queues[name]
        return self._local_queues[name]

    def create_stream(self, name: str, maxlen: int = 1000):
        """Pre-initialize a stream (Call from parent only)."""
        if name not in self._queues:
            if self.manager:
                with self._lock:
                    if name not in self._queues:
                        self._queues[name] = self.manager.Queue(maxsize=maxlen)
            else:
                logger.error(f"Cannot create stream {name} from child process.")

    def xadd(self, stream: str, data: Dict[str, Any], maxlen: int = 1000):
        """Emulate Redis XADD with improved throughput."""
        try:
            payload_str = data if isinstance(data, str) else json.dumps(data)
            wrapped = {"payload": payload_str, "ts": time.time()}

            q = self.get_queue(stream)
            try:
                q.put_nowait(wrapped)
            except queue.Full:
                try:
                    q.get_nowait()
                    q.put_nowait(wrapped)
                except (queue.Empty, queue.Full):
                    logger.debug("IPC Local Queue Saturation")
        except Exception as e:
            logger.error(f"IPC XADD Critical Fail on {stream}: {e}")

    def xread(self, streams: Dict[str, str], count: int = 50, block: int = 0) -> List[Any]:
        """Emulate Redis XREAD with batch processing."""
        results = []
        for stream_name in streams.keys():
            try:
                q = self.get_queue(stream_name)
                msgs = []
                for _ in range(count):
                    try:
                        val = q.get_nowait()
                        p = val.get("payload") if isinstance(val, dict) else val
                        if isinstance(p, str): p = p.encode('utf-8')
                        msgs.append(("id", {b'payload': p}))
                    except queue.Empty:
                        break
                if msgs:
                    results.append((stream_name, msgs))
            except Exception:
                continue
        return results

    def acquire_trading_lock(self, symbol: str, cooldown: int = 30) -> bool:
        """10260: Atomically acquire a trading lock for a symbol."""
        if not self._lock:
            logger.error("IPC Lock is None in acquire_trading_lock")
            return False
        with self._lock:
            now = time.time()
            last_trade = self._shared_state.get(f"trade_lock:{symbol}", 0)
            if now - last_trade < cooldown:
                return False
            self._shared_state[f"trade_lock:{symbol}"] = now
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
