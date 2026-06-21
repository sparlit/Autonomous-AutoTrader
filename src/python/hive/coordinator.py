import asyncio
import logging
import time
import os
import psutil
from typing import Dict, Any, List, Optional
from multiprocessing import Queue
from src.python.bridge.server import BridgeServer
from src.python.brains.registry import BrainRegistry
from src.python.brains.specialized import (
    MarketDataBrain, IndicatorBrain, TrendBrain,
    LiquidityBrain, RiskBrain, ExecutionBrain
)
from src.python.brains.consensus import MetaBrain
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_Orchestrator")

class HiveOrchestrator:
    """
    The Main Orchestrator (Process 1).
    Manages the 14+ process layout and routes messages via internal Queues.
    """

    def __init__(self):
        self.config = load_config()
        self.registry = BrainRegistry()
        self.meta_brain = MetaBrain(self.config.brains.consensus_threshold)

        # Central Message Bus
        self.brain_inputs: Dict[str, List[Queue]] = {}
        self.brain_output_queue = Queue()

        # Initialize MT5 Bridge
        self.server = BridgeServer(
            self.config.bridge.host,
            self.config.bridge.port,
            self.handle_client_message
        )

        self._initialize_brains()

    def _initialize_brains(self):
        """Configure 20 Logical Processor layout."""
        # 1. Market Data (2 Processes) - CPU 2-3
        self.brain_inputs["MarketData"] = [Queue(), Queue()]
        self.registry.register(MarketDataBrain("MarketData_1", self.brain_inputs["MarketData"][0], self.brain_output_queue, cpu_affinity=[2]))
        self.registry.register(MarketDataBrain("MarketData_2", self.brain_inputs["MarketData"][1], self.brain_output_queue, cpu_affinity=[3]))

        # 2. Indicators (3 Processes) - CPU 4-6
        self.brain_inputs["Indicator"] = [Queue(), Queue(), Queue()]
        self.registry.register(IndicatorBrain("Indicator_1", self.brain_inputs["Indicator"][0], self.brain_output_queue, cpu_affinity=[4]))
        self.registry.register(IndicatorBrain("Indicator_2", self.brain_inputs["Indicator"][1], self.brain_output_queue, cpu_affinity=[5]))
        self.registry.register(IndicatorBrain("Indicator_3", self.brain_inputs["Indicator"][2], self.brain_output_queue, cpu_affinity=[6]))

        # 3. Strategy Engines (4 Processes) - CPU 7-10
        self.brain_inputs["Trend"] = [Queue(), Queue(), Queue(), Queue()]
        self.registry.register(TrendBrain("Trend_1", self.brain_inputs["Trend"][0], self.brain_output_queue, cpu_affinity=[7]))
        self.registry.register(TrendBrain("Trend_2", self.brain_inputs["Trend"][1], self.brain_output_queue, cpu_affinity=[8]))
        self.registry.register(TrendBrain("Trend_3", self.brain_inputs["Trend"][2], self.brain_output_queue, cpu_affinity=[9]))
        self.registry.register(TrendBrain("Trend_4", self.brain_inputs["Trend"][3], self.brain_output_queue, cpu_affinity=[10]))

        # 4. Liquidity (Spare Pool)
        # For simplicity, we use one liquidity brain on a dedicated core
        self.brain_inputs["Liquidity"] = [Queue()]
        self.registry.register(LiquidityBrain("Liquidity_1", self.brain_inputs["Liquidity"][0], self.brain_output_queue, cpu_affinity=[11]))

        # 5. Risk Engine (2 Processes) - CPU 14-15
        self.brain_inputs["Risk"] = [Queue(), Queue()]
        self.registry.register(RiskBrain("Risk_1", self.brain_inputs["Risk"][0], self.brain_output_queue, cpu_affinity=[14]))
        self.registry.register(RiskBrain("Risk_2", self.brain_inputs["Risk"][1], self.brain_output_queue, cpu_affinity=[15]))

        # 6. Trade Execution (2 Processes) - CPU 16-17
        self.brain_inputs["Execution"] = [Queue(), Queue()]
        self.registry.register(ExecutionBrain("Execution_1", self.brain_inputs["Execution"][0], self.brain_output_queue, cpu_affinity=[16]))
        self.registry.register(ExecutionBrain("Execution_2", self.brain_inputs["Execution"][1], self.brain_output_queue, cpu_affinity=[17]))

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Load-balance incoming MT5 messages."""
        # Simple Round Robin for Market Data
        target = 0 if time.time() % 2 < 1 else 1
        self.brain_inputs["MarketData"][target].put(message)
        return {"t": "ACK", "s": "Orchestrator received"}

    async def run(self):
        """Launch the hive and start the event loop."""
        logger.info("Starting Phoenix Ascendant Orchestrator (Process 1)...")

        # Pin Orchestrator to CPU 1
        p = psutil.Process(os.getpid())
        try: p.cpu_affinity([1])
        except: pass

        # 1. Start all specialized processes
        self.registry.start_all()

        # 2. Start MT5 Bridge
        asyncio.create_task(self.server.start())

        # 3. Main Event Loop
        await self._main_orchestration_loop()

    async def _main_orchestration_loop(self):
        """Routes messages between brains with load balancing."""
        logger.info("Orchestration Loop Active.")
        counter = 0
        while True:
            try:
                if not self.brain_output_queue.empty():
                    event = self.brain_output_queue.get_nowait()
                    e_type = event.get("type")

                    if e_type == "MARKET_DATA":
                        # Fan-out to Indicators, Trend, and Liquidity
                        for q in self.brain_inputs["Indicator"]: q.put(event)
                        for q in self.brain_inputs["Trend"]: q.put(event)
                        for q in self.brain_inputs["Liquidity"]: q.put(event)

                    elif e_type in ["TREND", "INDICATORS", "LIQUIDITY"]:
                        decision = self.meta_brain.process_event(event)
                        if decision and decision["type"] == "SIGNAL":
                            # Load balance Risk
                            self.brain_inputs["Risk"][counter % 2].put(decision)
                            counter += 1

                    elif e_type == "VALIDATED_TRADE":
                        # Load balance Execution
                        self.brain_inputs["Execution"][counter % 2].put(event)
                        counter += 1

                    elif e_type == "EXECUTION_ORDER":
                        logger.info(f"Order Finalized: {event['symbol']} {event['action']}")

                else:
                    await asyncio.sleep(0.001)
            except Exception as e:
                logger.error(f"Orchestration Loop Error: {e}")
                await asyncio.sleep(0.1)

    def stop(self):
        """Graceful shutdown."""
        self.registry.stop_all()
