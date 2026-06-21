import asyncio
import logging
import os
import psutil
import time
import signal
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from multiprocessing import Process, Queue

logger = logging.getLogger("AAT_BaseBrain")

class BrainContract(ABC):
    """The strict contract every Brain must follow."""

    @abstractmethod
    def initialize(self):
        """Initial setup, dependency loading, and hardware optimization."""
        raise NotImplementedError()

    @abstractmethod
    async def run(self):
        """The main loop of the brain, processing events from the bus."""
        raise NotImplementedError()

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return health metrics (CPU, Memory, Latency)."""
        raise NotImplementedError()

class BaseBrain(Process, BrainContract):
    """
    A foundational Brain class that runs in its own process,
    manages its own lifecycle, and strictly adheres to the
    Single Responsibility Principle.
    """

    def __init__(self, name: str, input_queue: Queue, output_queue: Queue, cpu_affinity: Optional[List[int]] = None):
        Process.__init__(self)
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.cpu_affinity = cpu_affinity
        self.is_running = True
        self._last_heartbeat = time.time()
        self._processed_count = 0
        self._latency_sum = 0.0

    def initialize(self):
        """Default initialization: Set CPU affinity and logging."""
        p = psutil.Process(os.getpid())
        if self.cpu_affinity:
            try:
                p.cpu_affinity(self.cpu_affinity)
                logger.info(f"Brain {self.name} pinned to cores: {self.cpu_affinity}")
            except Exception as e:
                logger.warning(f"Could not set CPU affinity for {self.name}: {e}")

        # Isolated logging for each brain
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s - {self.name} - %(levelname)s - %(message)s"
        )
        logger.info(f"Brain {self.name} initialized in PID {os.getpid()}")

    def run(self):
        """Process entry point."""
        self.initialize()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)

        asyncio.run(self._main_loop())

    async def _main_loop(self):
        """Async main loop for I/O and processing."""
        logger.info(f"Brain {self.name} entering main loop.")
        while self.is_running:
            try:
                # Non-blocking check for messages (simulating Redis Stream read)
                if not self.input_queue.empty():
                    msg = self.input_queue.get_nowait()
                    start_time = time.perf_counter()

                    result = await self.process(msg)

                    if result:
                        self.publish(result)

                    latency = time.perf_counter() - start_time
                    self._latency_sum += latency
                    self._processed_count += 1
                    self._last_heartbeat = time.time()
                else:
                    await asyncio.sleep(0.001) # Yield to CPU
            except Exception as e:
                logger.error(f"Brain {self.name} Loop Error: {e}")
                await asyncio.sleep(0.1)

    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Specific logic for this brain."""
        raise NotImplementedError()

    def publish(self, result: Dict[str, Any]):
        """Publish results to the output stream (Orchestrator)."""
        # Ensure name is attached for traceability
        result['source'] = self.name
        result['timestamp'] = time.time()
        self.output_queue.put(result)

    def health(self) -> Dict[str, Any]:
        """Return process health statistics."""
        p = psutil.Process(os.getpid())
        avg_latency = self._latency_sum / self._processed_count if self._processed_count > 0 else 0
        return {
            "name": self.name,
            "pid": os.getpid(),
            "cpu_percent": p.cpu_percent(),
            "memory_mb": p.memory_info().rss / 1024 / 1024,
            "processed": self._processed_count,
            "avg_latency_ms": avg_latency * 1000,
            "alive": self.is_alive(),
            "last_heartbeat": self._last_heartbeat
        }

    def _handle_exit(self, signum, frame):
        logger.info(f"Brain {self.name} received exit signal. Shutting down...")
        self.is_running = False
