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
from fakeredis import FakeRedis

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
    def initialize(self):
        """12001: Hardware and dependency setup."""
        raise NotImplementedError()
    @abstractmethod
    async def run(self):
        """12002: Process main event loop."""
        raise NotImplementedError()
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """12003: Collect process health metrics."""
        raise NotImplementedError()

class BaseBrain(Process, BrainContract):
    """
    12004: Foundation class for isolated brain processes.
    Reinforced with execution timeouts and bounded stream management.
    """

    def __init__(self, name: str, cpu_affinity: Optional[List[int]] = None):
        Process.__init__(self)
        self.name = name
        self.cpu_affinity = cpu_affinity
        self.is_running = True
        self._last_heartbeat = time.time()
        self._processed_count = 0
        self._latency_sum = 0.0
        self.redis = FakeRedis()
        self.max_execution_time = 0.1 # 100ms hard deadline (12101)
        self.stream_max_len = 1000 # Bounded streams to prevent OOM (12102)

    def initialize(self):
        """12005: Hardware and dependency setup."""
        p = psutil.Process(os.getpid())
        if self.cpu_affinity:
            try:
                p.cpu_affinity(self.cpu_affinity)
                logger.info(f"Brain {self.name} pinned to cores: {self.cpu_affinity}")
            except Exception as e:
                logger.warning(f"Affinity fail for {self.name}: {e}")

        logging.basicConfig(level=logging.INFO, format=f"%(asctime)s - {self.name} - %(levelname)s - %(message)s")
        logger.info(f"Brain {self.name} online (PID {os.getpid()})")

    def run(self):
        """12006: Process entry point."""
        self.initialize()
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        """12007: Async execution loop with timeouts and backpressure."""
        stream_name = f"stream:{self.name}"
        while self.is_running:
            try:
                # 12103: Drop old ticks if backlog exists (Coalescing/Backpressure)
                messages = self.redis.xread({stream_name: '0'}, count=10, block=1)
                if messages:
                    for stream, msgs in messages:
                        # Only process the LATEST message if it's high-frequency data
                        # to ensure low-latency execution (12104)
                        latest_msg = msgs[-1]
                        msg_id, data = latest_msg

                        event = json.loads(data[b'payload'])
                        start_time = time.perf_counter()

                        try:
                            # 12105: Hard execution deadline
                            result = await asyncio.wait_for(self.process(event), timeout=self.max_execution_time)
                            if result: self.publish(result)
                        except asyncio.TimeoutError:
                            logger.error(f"Brain {self.name} TIMEOUT on msg {msg_id}. Dropping result.")

                        # 12106: Explicitly clear processed items
                        for m_id, _ in msgs:
                            self.redis.xdel(stream_name, m_id)

                        self._latency_sum += (time.perf_counter() - start_time)
                        self._processed_count += 1
                else:
                    await asyncio.sleep(0.0001) # Yield to CPU
            except Exception as e:
                logger.error(f"Brain {self.name} Error: {e}")
                await asyncio.sleep(0.1)

    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """12009: Domain-specific logic."""
        raise NotImplementedError()

    def publish(self, result: Dict[str, Any]):
        """12010: Publish to the Orchestrator stream with bounded length."""
        result['source'] = self.name; result['timestamp'] = time.time()
        payload = json.dumps(result)
        # 12107: Use MAXLEN for backpressure in message bus
        self.redis.xadd("stream:orchestrator", {"payload": payload}, maxlen=self.stream_max_len)

    def health(self) -> Dict[str, Any]:
        """12011: Collect health metrics."""
        p = psutil.Process(os.getpid()); avg_latency = self._latency_sum / self._processed_count if self._processed_count > 0 else 0
        return {"name": self.name, "pid": os.getpid(), "cpu": p.cpu_percent(), "mem": p.memory_info().rss / 1024 / 1024, "count": self._processed_count, "latency": avg_latency * 1000}

    def _handle_exit(self, signum, frame):
        self.is_running = False
