# Version: V3.1.3-AUTONOMOUS (Hardened RESTRUCTURE)
import multiprocessing as mp
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from shared.memory import SharedState, MessageQueue
from shared.config_manager import load_aat_config

logger = logging.getLogger("AAT_Brain")

class InstitutionalBrain(mp.Process, ABC):
    """12000: Base class for institutional specialized brains."""
    def __init__(self, name: str, shared_state: SharedState, input_q: MessageQueue, output_q: MessageQueue):
        mp.Process.__init__(self)
        self.brain_name = name
        self.shm = shared_state
        self.iq = input_q
        self.oq = output_q
        self.is_running = True

    def run(self):
        logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - {self.brain_name} - %(levelname)s - %(message)s')
        logger.info(f"Brain {self.brain_name} launched.")
        try:
            asyncio.run(self._async_run())
        except Exception as e:
            logger.error(f"Brain {self.brain_name} fatal error: {e}")

    async def _async_run(self):
        config = load_aat_config()
        tick = config.brains.tick_rate_ms / 1000.0
        await self.on_init()
        while self.is_running:
            msgs = self.iq.pop_all()
            for msg in msgs:
                start_time = time.perf_counter()
                result = await self.process(msg)
                if result:
                    result['brain'] = self.brain_name
                    result['latency'] = (time.perf_counter() - start_time) * 1000
                    self.oq.push(result)

            self.shm.update_key(f"health:{self.brain_name}", {"t": time.time(), "status": "ALIVE"})
            await asyncio.sleep(tick)

    async def on_init(self):
        """Institutional hook for brain startup."""
        logger.debug(f"Brain {self.brain_name} initialized.")

    @abstractmethod
    async def process(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

class SMCBrain(InstitutionalBrain):
    async def process(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if msg.get('t') != 'DATA': return None
        return {"type": "SIGNAL", "symbol": msg.get('s'), "score": 0.85, "direction": "BUY", "logic": "BOS_DETECTED"}

class VSABrain(InstitutionalBrain):
    async def process(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if msg.get('t') != 'DATA': return None
        return {"type": "SIGNAL", "symbol": msg.get('s'), "score": 0.70, "direction": "BUY", "logic": "HIGH_VOL_CHURN"}
