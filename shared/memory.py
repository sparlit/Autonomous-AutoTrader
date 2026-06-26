# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
import ujson as json
import multiprocessing as mp
from multiprocessing import shared_memory
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger("AAT_SharedMemory")

class SharedState:
    """10200: Ultra-Low Latency shared memory state for real-time telemetry."""
    def __init__(self, name: str = "aat_shared_state", size: int = 1024 * 1024):
        self.size = size
        self.name = name
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name)

        self.lock = mp.Lock()

    def set_data(self, data: Dict[str, Any]):
        serialized = json.dumps(data).encode('utf-8')
        if len(serialized) > self.size - 4:
            raise MemoryError(f"SharedState {self.name}: Data exceeds buffer size.")
        with self.lock:
            self.shm.buf[:4] = len(serialized).to_bytes(4, 'big')
            self.shm.buf[4:4+len(serialized)] = serialized

    def get_data(self) -> Dict[str, Any]:
        with self.lock:
            length = int.from_bytes(self.shm.buf[:4], 'big')
            if length == 0: return {}
            data_bytes = self.shm.buf[4:4+length].tobytes()
            try:
                return json.loads(data_bytes)
            except Exception as e:
                logger.error(f"SharedState Read Error in {self.name}: {e}")
                return {}

    def update_key(self, key: str, value: Any):
        with self.lock:
            data = self.get_data()
            data[key] = value
            self.set_data(data)

    def cleanup(self):
        try:
            self.shm.close()
            self.shm.unlink()
        except Exception as e:
            logger.debug(f"SHM Cleanup skipped for {self.name}: {e}")

class MessageQueue:
    """10205: Circular buffer message queue using shared memory."""
    def __init__(self, name: str, size: int = 1024 * 512):
        self.name = f"aat_q_{name}"
        self.size = size
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name)
        self.lock = mp.Lock()

    def push(self, message: Dict[str, Any]):
        payload = json.dumps(message).encode('utf-8')
        p_len = len(payload)
        with self.lock:
            w_pos = int.from_bytes(self.shm.buf[0:4], 'big')
            if w_pos == 0: w_pos = 8
            if w_pos + 4 + p_len > self.size: w_pos = 8
            self.shm.buf[w_pos:w_pos+4] = p_len.to_bytes(4, 'big')
            self.shm.buf[w_pos+4:w_pos+4+p_len] = payload
            self.shm.buf[0:4] = (w_pos + 4 + p_len).to_bytes(4, 'big')

    def pop_all(self) -> List[Dict[str, Any]]:
        messages = []
        with self.lock:
            w_pos = int.from_bytes(self.shm.buf[0:4], 'big')
            r_pos = int.from_bytes(self.shm.buf[4:8], 'big')
            if r_pos == 0: r_pos = 8
            curr = r_pos
            while curr < w_pos:
                p_len = int.from_bytes(self.shm.buf[curr:curr+4], 'big')
                if p_len == 0: break
                payload = self.shm.buf[curr+4:curr+4+p_len].tobytes()
                try:
                    messages.append(json.loads(payload))
                except Exception as e:
                    logger.error(f"Queue Pop Serialization Error in {self.name}: {e}")
                curr += 4 + p_len
            self.shm.buf[4:8] = w_pos.to_bytes(4, 'big')
        return messages

    def cleanup(self):
        try:
            self.shm.close()
            self.shm.unlink()
        except Exception as e:
            logger.debug(f"Queue Cleanup skipped for {self.name}: {e}")
