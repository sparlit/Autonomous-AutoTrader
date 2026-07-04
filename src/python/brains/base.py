import asyncio
import logging
import os
import psutil
import time
import signal
import ujson as json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
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
    V4.0: Foundation class for isolated brain processes.
    Enhanced with MTF-Parallel Dispatching and high-performance batch processing.
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
        self.max_execution_time = 0.2 # 200ms deadline for V4.0 Parallel tasks
        self.stream_max_len = 2000 # Increased buffer for MTF bursts

    async def initialize(self):
        """12005: Hardware and dependency setup."""
        p = psutil.Process(os.getpid())
        if self.cpu_affinity:
            try:
                p.cpu_affinity(self.cpu_affinity)
            except Exception as e:
                logger.debug(f"Affinity fail for {self.name}: {e}")
        self._last_activity = time.time()

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
        logger.info(f"🧠 Brain {self.name} online (V4.0 Parallel Engine Active).")
        await self._main_loop()

    async def _main_loop(self):
        """V4.0 Parallel Execution Engine: Processes batches in parallel."""
        stream_name = f"stream:{self.name}"
        last_health_report = 0
        while self.is_running:
            try:
                now = time.time()
                if now - last_health_report > 10:
                    if self.ipc:
                        self.ipc.set_state(f"brain_health:{self.name}", self.health())
                    last_health_report = now

                if self.ipc:
                    # Read larger batches for parallel processing
                    messages = self.ipc.xread({stream_name: '0'}, count=50)
                    if messages:
                        tasks = []
                        for stream, msgs in messages:
                            for msg_id, data in msgs:
                                event = json.loads(data[b'payload'])
                                tasks.append(self._safe_process(event))

                        if tasks:
                            results = await asyncio.gather(*tasks, return_exceptions=True)
                            for res in results:
                                if isinstance(res, Exception):
                                    logger.error(f"Brain {self.name} Task Error: {res}")
                                elif res:
                                    if isinstance(res, list):
                                        for r in res: self.publish(r)
                                    else:
                                        self.publish(res)

                        await asyncio.sleep(0.001) # Ultra-low latency breath
                    else:
                        await asyncio.sleep(0.01) # Faster polling for V4.0
                else:
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Brain {self.name} Loop Error: {e}")
                await asyncio.sleep(0.1)

    async def _safe_process(self, event: Dict[str, Any]) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        start_time = time.perf_counter()
        try:
            res = await asyncio.wait_for(self.process(event), timeout=self.max_execution_time)
            self._latency_sum += (time.perf_counter() - start_time)
            self._processed_count += 1
            return res
        except asyncio.TimeoutError:
            logger.warning(f"Brain {self.name} TIMEOUT on {event.get('type')}")
            return None
        except Exception as e:
            logger.error(f"Brain {self.name} process error: {e}")
            return None

    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        raise NotImplementedError()

    def publish(self, result: Dict[str, Any]):
        """12010: Publish to the Orchestrator stream with bounded length."""
        if not self.ipc: return
        result['source'] = self.name; result['timestamp'] = time.time()
        self.ipc.xadd("stream:orchestrator", result, maxlen=self.stream_max_len)

    def publish_state(self, symbol: str, state: Dict[str, Any]):
        """12012: Publish detailed per-symbol internal state for Glass-Box telemetry."""
        if not self.ipc: return
        state['ts'] = time.time()
        self.ipc.set_state(f"brain_state:{self.name}:{symbol}", state)

    def health(self) -> Dict[str, Any]:
        """12011: Collect health metrics."""
        p = psutil.Process(os.getpid()); avg_latency = self._latency_sum / self._processed_count if self._processed_count > 0 else 0
        return {
            "name": self.name, "pid": os.getpid(), "cpu": p.cpu_percent(),
            "mem": p.memory_info().rss / 1024 / 1024, "count": self._processed_count,
            "latency": avg_latency * 1000, "last_heartbeat": time.time()
        }

    def _handle_exit(self, signum, frame):
        self.is_running = False
