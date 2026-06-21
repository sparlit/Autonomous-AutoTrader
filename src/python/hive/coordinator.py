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
    LiquidityBrain, RiskBrain, ExecutionBrain,
    RegimeBrain, ContrarianBrain, MemoryBrain,
    NewsRiskBrain, MonitoringBrain
)
from src.python.brains.consensus import MetaBrain
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_Orchestrator")

class HiveOrchestrator:
    """
    Process 1 - The Main Orchestrator.
    Manages the 20 Logical Processor layout and routes messages via internal Queues.
    Communication is strictly via the message bus.
    """

    def __init__(self):
        self.config = load_config()
        self.registry = BrainRegistry()

        # Message Bus Channels
        self.brain_inputs: Dict[str, List[Queue]] = {}
        self.output_queue = Queue()

        # Initialize MT5 Bridge
        self.server = BridgeServer(
            self.config.bridge.host,
            self.config.bridge.port,
            self.handle_client_message
        )

        self._initialize_brains()

    def _initialize_brains(self):
        # 1. Market Data - CPU 2-3
        self.brain_inputs["MarketData"] = [Queue(), Queue()]
        self.registry.register(MarketDataBrain("MarketData_1", self.brain_inputs["MarketData"][0], self.output_queue, cpu_affinity=[2]))
        self.registry.register(MarketDataBrain("MarketData_2", self.brain_inputs["MarketData"][1], self.output_queue, cpu_affinity=[3]))

        # 2. Indicators - CPU 4-6
        self.brain_inputs["Indicator"] = [Queue(), Queue(), Queue()]
        self.registry.register(IndicatorBrain("Indicator_1", self.brain_inputs["Indicator"][0], self.output_queue, cpu_affinity=[4]))
        self.registry.register(IndicatorBrain("Indicator_2", self.brain_inputs["Indicator"][1], self.output_queue, cpu_affinity=[5]))
        self.registry.register(IndicatorBrain("Indicator_3", self.brain_inputs["Indicator"][2], self.output_queue, cpu_affinity=[6]))

        # 3. Strategy Engines - CPU 7-10
        self.brain_inputs["Trend"] = [Queue(), Queue()]
        self.registry.register(TrendBrain("Trend_1", self.brain_inputs["Trend"][0], self.output_queue, cpu_affinity=[7]))
        self.registry.register(TrendBrain("Trend_2", self.brain_inputs["Trend"][1], self.output_queue, cpu_affinity=[8]))
        self.brain_inputs["Liquidity"] = [Queue()]
        self.registry.register(LiquidityBrain("Liquidity_1", self.brain_inputs["Liquidity"][0], self.output_queue, cpu_affinity=[9]))
        self.brain_inputs["Regime"] = [Queue()]
        self.registry.register(RegimeBrain("Regime_1", self.brain_inputs["Regime"][0], self.output_queue, cpu_affinity=[10]))

        # 4. Meta Brain - CPU 11
        self.brain_inputs["Meta"] = [Queue()]
        self.registry.register(MetaBrain("Meta_1", self.brain_inputs["Meta"][0], self.output_queue, cpu_affinity=[11], threshold=self.config.brains.consensus_threshold))

        # 5. Veto & News - CPU 12-13
        self.brain_inputs["Contrarian"] = [Queue()]
        self.registry.register(ContrarianBrain("Contrarian_1", self.brain_inputs["Contrarian"][0], self.output_queue, cpu_affinity=[12]))
        self.brain_inputs["NewsRisk"] = [Queue()]
        self.registry.register(NewsRiskBrain("NewsRisk_1", self.brain_inputs["NewsRisk"][0], self.output_queue, cpu_affinity=[13]))

        # 6. Risk Engine - CPU 14-15
        self.brain_inputs["Risk"] = [Queue(), Queue()]
        self.registry.register(RiskBrain("Risk_1", self.brain_inputs["Risk"][0], self.output_queue, cpu_affinity=[14]))
        self.registry.register(RiskBrain("Risk_2", self.brain_inputs["Risk"][1], self.output_queue, cpu_affinity=[15]))

        # 7. Trade Execution - CPU 16-17
        self.brain_inputs["Execution"] = [Queue(), Queue()]
        self.registry.register(ExecutionBrain("Execution_1", self.brain_inputs["Execution"][0], self.output_queue, cpu_affinity=[16]))
        self.registry.register(ExecutionBrain("Execution_2", self.brain_inputs["Execution"][1], self.output_queue, cpu_affinity=[17]))

        # 8. Monitoring & Memory - CPU 18-19
        self.brain_inputs["Monitoring"] = [Queue()]
        self.registry.register(MonitoringBrain("Monitoring_1", self.brain_inputs["Monitoring"][0], self.output_queue, cpu_affinity=[18]))
        self.brain_inputs["Memory"] = [Queue()]
        self.registry.register(MemoryBrain("Memory_1", self.brain_inputs["Memory"][0], self.output_queue, cpu_affinity=[19]))

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        target = 0 if time.time() % 2 < 1 else 1
        self.brain_inputs["MarketData"][target].put(message)
        return {"t": "ACK", "s": "Forwarded to Brains"}

    async def run(self):
        logger.info("🌌 Phoenix Ascendant Orchestrator Online.")
        p = psutil.Process(os.getpid());
        try: p.cpu_affinity([1])
        except: raise

        self.registry.start_all()
        asyncio.create_task(self.server.start())
        await self._main_orchestration_loop()

    async def _main_orchestration_loop(self):
        counter = 0
        while True:
            try:
                if not self.output_queue.empty():
                    event = self.output_queue.get_nowait()
                    e_type = event.get("type")

                    # CHANNEL ROUTING
                    if e_type == "MARKET_DATA":
                        # Refresh Vetoes
                        self.brain_inputs["Meta"][0].put({"type": "MARKET_DATA_REFRESH", "symbol": event["symbol"]})
                        # Analysts Fan-out
                        for b in ["Indicator", "Trend", "Liquidity", "Regime"]:
                            for q in self.brain_inputs[b]: q.put(event)
                        self.brain_inputs["NewsRisk"][0].put(event)

                    elif e_type in ["TREND", "INDICATORS", "LIQUIDITY", "REGIME", "VETO", "NEWS_VETO"]:
                        # Forward all partial signals to MetaBrain
                        self.brain_inputs["Meta"][0].put(event)

                    elif e_type == "SIGNAL":
                        # Veto & Risk Chain
                        self.brain_inputs["Contrarian"][0].put(event)
                        self.brain_inputs["Risk"][counter % 2].put(event)
                        counter += 1

                    elif e_type == "VALIDATED_TRADE":
                        self.brain_inputs["Execution"][counter % 2].put(event)
                        counter += 1

                    elif e_type == "EXECUTION_ORDER":
                        self.brain_inputs["Memory"][0].put(event)
                        logger.info(f"Broadcast: {event['symbol']} {event['action']}")

                else:
                    await asyncio.sleep(0.001)
            except Exception as e:
                logger.error(f"Orchestrator Error: {e}")
                await asyncio.sleep(0.1)

    def stop(self):
        self.registry.stop_all()
