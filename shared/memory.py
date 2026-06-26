# Version: V3.1.0-AUTONOMOUS (Hardened RESTRUCTURE)
import mmap
import ujson as json
import multiprocessing as mp
from multiprocessing import shared_memory
from typing import Dict, Any, Optional, List
import time
import ctypes

class SharedState:
    """10200: Ultra-Low Latency shared memory state for real-time telemetry."""
    def __init__(self, size: int = 1024 * 1024): # 1MB default
        self.size = size
        try:
            self.shm = shared_memory.SharedMemory(name="aat_shared_state", create=True, size=size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name="aat_shared_state")

        self.lock = mp.Lock()
        self._initialize_buffer()

    def _initialize_buffer(self):
        with self.lock:
            # Initialize with empty JSON dict if new
            existing = self.shm.buf[:10].tobytes()
            if b"{" not in existing:
                self.set_data({})

    def set_data(self, data: Dict[str, Any]):
        """10201: Atomic JSON update to shared memory."""
        serialized = json.dumps(data).encode('utf-8')
        if len(serialized) > self.size - 4:
            raise MemoryError("SharedState: Data exceeds allocated buffer size.")

        with self.lock:
            # Write length prefix (4 bytes)
            self.shm.buf[:4] = len(serialized).to_bytes(4, 'big')
            self.shm.buf[4:4+len(serialized)] = serialized

    def get_data(self) -> Dict[str, Any]:
        """10202: Fast read from shared memory."""
        with self.lock:
            length = int.from_bytes(self.shm.buf[:4], 'big')
            if length == 0: return {}
            data_bytes = self.shm.buf[4:4+length].tobytes()
            try:
                return json.loads(data_bytes)
            except Exception:
                return {}

    def update_key(self, key: str, value: Any):
        """10203: Partial update helper."""
        with self.lock:
            data = self.get_data()
            data[key] = value
            self.set_data(data)

    def cleanup(self):
        """10204: Resource release."""
        self.shm.close()
        try:
            self.shm.unlink()
        except Exception:
            pass

class MessageQueue:
    """10205: Circular buffer message queue using shared memory for lock-free-ish communication."""
    def __init__(self, name: str, size: int = 1024 * 512): # 512KB
        self.name = f"aat_q_{name}"
        self.size = size
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name)

        # Buffer Layout: [WritePos (4)] [ReadPos (4)] [Data...]
        self.lock = mp.Lock()

    def push(self, message: Dict[str, Any]):
        """10206: Push message into circular buffer."""
        payload = json.dumps(message).encode('utf-8')
        p_len = len(payload)

        with self.lock:
            w_pos = int.from_bytes(self.shm.buf[0:4], 'big')
            r_pos = int.from_bytes(self.shm.buf[4:8], 'big')

            # Simple linear write for now, wrapping if needed
            # [4 bytes len][payload]
            if w_pos + 4 + p_len > self.size:
                w_pos = 8 # Wrap to beginning (after indices)

            self.shm.buf[w_pos : w_pos+4] = p_len.to_bytes(4, 'big')
            self.shm.buf[w_pos+4 : w_pos+4+p_len] = payload

            new_w_pos = w_pos + 4 + p_len
            self.shm.buf[0:4] = new_w_pos.to_bytes(4, 'big')

    def pop_all(self) -> List[Dict[str, Any]]:
        """10207: Drain all messages since last read."""
        messages = []
        with self.lock:
            w_pos = int.from_bytes(self.shm.buf[0:4], 'big')
            r_pos = int.from_bytes(self.shm.buf[4:8], 'big')

            if r_pos == 0: r_pos = 8 # Init

            # Basic linear drain
            curr = r_pos
            while curr < w_pos:
                p_len = int.from_bytes(self.shm.buf[curr:curr+4], 'big')
                if p_len == 0: break

                payload = self.shm.buf[curr+4:curr+4+p_len].tobytes()
                try:
                    messages.append(json.loads(payload))
                except:
                    pass
                curr += 4 + p_len

            self.shm.buf[4:8] = w_pos.to_bytes(4, 'big')
        return messages

    def cleanup(self):
        self.shm.close()
        try: self.shm.unlink()
        except: pass
