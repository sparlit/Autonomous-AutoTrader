import asyncio
import logging
import os
import psutil
import time
import signal
import ujson as json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from multiprocessing import Process
from pydantic import BaseModel

logger = logging.getLogger("AAT_BaseBrain")

class SignalPayload(BaseModel):
    """12000: Standardized strategy signal output."""
    symbol: str
    timeframe: int
    direction: int
    confidence: float
    strategy_name: str
    magic: int

class BrainContract(ABC):
    """The strict contract every Brain must follow."""
    @abstractmethod
    async def initialize(self):
        raise NotImplementedError()
    @abstractmethod
    def run(self):
        raise NotImplementedError()
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        raise NotImplementedError()

class BaseBrain(Process, BrainContract):
    """
    12004: Foundation class for isolated brain processes.
    Reinforced with execution timeouts and bounded stream management.
    """

    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None, ipc: Any = None):
        Process.__init__(self)
        self.name = name
        self.cpu_affinity = cpu_affinity
        self.ipc = ipc
        self.is_running = True
        self._processed_count = 0
        self._latency_sum = 0.0
        self._last_activity = 0.0
        self.max_execution_time = 0.1 # 100ms hard deadline (12101)
        self.stream_max_len = 1000 # Bounded streams to prevent OOM (12102)
        self._queue_ref = None

    async def initialize(self):
        """12005: Hardware and dependency setup."""
        p = psutil.Process(os.getpid())
        if self.cpu_affinity:
            try:
                p.cpu_affinity(self.cpu_affinity)
            except Exception as e:
                logger.debug(f"Affinity fail for {self.name}: {e}")
        self._last_activity = time.time()
        if self.ipc:
            # Pre-cache the queue reference in the child process
            self._queue_ref = self.ipc.get_queue(f"stream:{self.name}")

    def run(self):
        """12006: Process entry point."""
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)
        try:
            asyncio.run(self._async_run())
        except Exception as e:
            logger.error(f"Brain {self.name} crashed: {e}")

    async def _async_run(self):
        await self.initialize()
        logger.info(f"🧠 Brain {self.name} online and active.")
        await self._main_loop()

    async def _main_loop(self):
        """12007: Async execution loop with timeouts and backpressure."""
        stream_name = f"stream:{self.name}"
        last_health_report = 0
        while self.is_running:
            try:
                now = time.time()
                # Periodic health reporting to shared state
                if now - last_health_report > 5:
                    if self.ipc:
                        self.ipc.set_state(f"brain_health:{self.name}", self.health())
                    last_health_report = now

                if self.ipc:
                    # 10245: Process ALL pending messages, don't drop updates.
                    messages = self.ipc.xread({stream_name: '0'}, count=50, block=1)
                    if messages:
                        for stream, msgs in messages:
                            latest_msg = msgs[-1]
                            msg_id, data = latest_msg

                            event = json.loads(data[b'payload'])
                            start_time = time.perf_counter()

                            try:
                                result = await asyncio.wait_for(self.process(event), timeout=self.max_execution_time)
                                if result: self.publish(result)
                            except asyncio.TimeoutError:
                                logger.error(f"Brain {self.name} TIMEOUT on msg {msg_id}. Dropping result.")

                            self.ipc.xdel(stream_name, msg_id)
                            self._latency_sum += (time.perf_counter() - start_time)
                            self._processed_count += 1
                    else:
                        await asyncio.sleep(0.001)
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Brain {self.name} Loop Error: {e}")
                await asyncio.sleep(0.1)

    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

    def publish(self, result: Dict[str, Any]):
        """12010: Publish to the Orchestrator stream with bounded length."""
        if not self.ipc: return
        result['source'] = self.name; result['timestamp'] = time.time()
        payload = json.dumps(result)
        self.ipc.xadd("stream:orchestrator", {"payload": payload}, maxlen=self.stream_max_len)

    def health(self) -> Dict[str, Any]:
        """12011: Collect health metrics."""
        p = psutil.Process(os.getpid()); avg_latency = self._latency_sum / self._processed_count if self._processed_count > 0 else 0
        return {
            "name": self.name, "pid": os.getpid(), "cpu": p.cpu_percent(),
            "mem": p.memory_info().rss / 1024 / 1024, "count": self._processed_count,
            "latency": avg_latency * 1000, "last_seen": self._last_activity,
            "last_heartbeat": time.time()
        }

    def _handle_exit(self, signum, frame):
        self.is_running = False
