import asyncio
import ujson as json
import logging
import time
import os
import psutil
import subprocess
from typing import Dict, Any, List, Optional

from src.python.hive.config import load_config
from src.python.hive.ipc import get_ipc
from src.python.brains.registry import BrainRegistry
from src.python.brains.base import BaseBrain
from src.python.brains.specialized import (
    MarketDataBrain, IndicatorBrain, TrendBrain, LiquidityBrain,
    MomentumBrain, RegimeBrain, NewsRiskBrain,
    ContrarianBrain, CorrelationBrain, RiskBrain, ExecutionBrain,
    MemoryBrain, MonitoringBrain, AnomalyBrain, PortfolioBrain, StructureBrain
)
from src.python.brains.consensus import MetaBrain
from src.python.bridge.server import BridgeServer
from src.python.bridge.dashboards.native_gui import NativeDashboard
from src.python.bridge.dashboards.web_server import WebDashboard

logger = logging.getLogger("AAT_Orchestrator")

class HiveCoordinator:
    """Legacy alias for backward compatibility."""
    def __init__(self):
        self.config = load_config()
        self.registry = BrainRegistry()
        self.risk_manager = RiskManager(self.config)
        self.agent_states = {}
        self.orchestrator = HiveOrchestrator()

    async def run(self):
        await self.orchestrator.run()

class HiveOrchestrator:
    """10236: Reinforced Bayesian Orchestrator - Master Pro Edition."""
    def __init__(self):
        self.config = load_config()
        self.registry = BrainRegistry()
        self.ipc = get_ipc()
        self.brain_inputs: Dict[str, List[str]] = {}
        self.server = BridgeServer(
            self.config.bridge.host, self.config.bridge.port, self.handle_client_message
        )
        self.risk_manager = RiskManager(self.config)
        self._initialize_brains()
        self._initialize_ipc_queues()
        self._initialize_dashboards()

    def _initialize_brains(self):
        self.registry.register(MarketDataBrain("MarketData_1", cpu_affinity=[2], ipc=self.ipc))
        self.registry.register(MarketDataBrain("MarketData_2", cpu_affinity=[3], ipc=self.ipc))
        self.registry.register(IndicatorBrain("Indicator_1", cpu_affinity=[4], ipc=self.ipc))
        self.registry.register(IndicatorBrain("Indicator_2", cpu_affinity=[5], ipc=self.ipc))
        self.registry.register(IndicatorBrain("Indicator_3", cpu_affinity=[6], ipc=self.ipc))
        self.registry.register(TrendBrain("Trend_1", cpu_affinity=[7], ipc=self.ipc))
        self.registry.register(TrendBrain("Trend_2", cpu_affinity=[8], ipc=self.ipc))
        self.registry.register(LiquidityBrain("Liquidity_1", cpu_affinity=[9], ipc=self.ipc))
        self.registry.register(MomentumBrain("Momentum_1", cpu_affinity=[10], ipc=self.ipc))
        self.registry.register(RegimeBrain("Regime_1", cpu_affinity=[11], ipc=self.ipc))
        self.registry.register(MetaBrain("Meta_1", cpu_affinity=[12], threshold=self.config.brains.consensus_threshold, ipc=self.ipc))
        self.registry.register(NewsRiskBrain("NewsRisk_1", cpu_affinity=[13], ipc=self.ipc))
        self.registry.register(ContrarianBrain("Contrarian_1", cpu_affinity=[14], ipc=self.ipc))
        self.registry.register(CorrelationBrain("Correlation_1", cpu_affinity=[15], ipc=self.ipc))
        self.registry.register(RiskBrain("Risk_1", cpu_affinity=[16], ipc=self.ipc))
        self.registry.register(RiskBrain("Risk_2", cpu_affinity=[17], ipc=self.ipc))
        self.registry.register(ExecutionBrain("Execution_1", cpu_affinity=[18], ipc=self.ipc))
        self.registry.register(ExecutionBrain("Execution_2", cpu_affinity=[19], ipc=self.ipc))
        self.registry.register(MemoryBrain("Memory_1", cpu_affinity=[2], ipc=self.ipc))
        self.registry.register(MonitoringBrain("Monitoring_1", cpu_affinity=[3], ipc=self.ipc))
        self.registry.register(AnomalyBrain("Anomaly_1", cpu_affinity=[4], ipc=self.ipc))
        self.registry.register(PortfolioBrain("Portfolio_1", cpu_affinity=[5], ipc=self.ipc))
        self.registry.register(StructureBrain("Structure_1", cpu_affinity=[6], ipc=self.ipc))

    def _initialize_ipc_queues(self):
        """Pre-initialize all queues in the parent process to avoid child creation race."""
        for name in self.registry._brains.keys():
            self.ipc.get_queue(f"stream:{name}")
        self.ipc.get_queue("stream:orchestrator")

    def _initialize_ipc_queues(self):
        queues = [
            "stream:orchestrator", "stream:MarketData_1", "stream:MarketData_2",
            "stream:Indicator_1", "stream:Indicator_2", "stream:Indicator_3",
            "stream:Trend_1", "stream:Trend_2", "stream:Liquidity_1", "stream:Liquidity_2",
            "stream:Regime_1", "stream:Meta_1", "stream:Contrarian_1", "stream:NewsRisk_1",
            "stream:Risk_1", "stream:Risk_2", "stream:Execution_1", "stream:Execution_2",
            "stream:Memory_1", "stream:Monitoring_1", "stream:Anomaly_1", "stream:Portfolio_1"
        ]
        for q_name in queues:
            self._queue_cache[q_name] = self.ipc.get_queue(q_name)

    def _initialize_dashboards(self):
        self.native_dash = NativeDashboard(ipc=self.ipc)
        self.web_dash = WebDashboard(ipc=self.ipc, port=self.config.bridge.dashboard_port)

    def _get_queue(self, name: str):
        if name not in self._queue_cache:
            self._queue_cache[name] = self.ipc.get_queue(name)
        return self._queue_cache[name]

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "HB":
            self.ipc.set_state("account_stats", {
                "equity": message.get("e", 0),
                "drawdown": message.get("d", 0),
                "spread": message.get("sp", 0),
                "candle_timer": message.get("ct", "--:--")
            })

        target = f"stream:MarketData_{1 if time.time() % 2 < 1 else 2}"
        self.ipc.xadd(target, {"payload": json.dumps(message)}, maxlen=1000)
        return {"t": "ACK", "s": "Forwarded to stream"}

    async def run(self):
        p = psutil.Process(os.getpid())
        try:
            p.cpu_affinity([1])
        except Exception:
            logger.warning("CPU affinity failed for Orchestrator")

        self.native_dash.start()
        self.web_dash.start()

        # Start the MT5 bridge server
        server_task = asyncio.create_task(self.server.start())

    async def _main_orchestration_loop(self):
        """10238: Shared IPC central routing loop."""
        counter = 0
        last_stat_update = 0
        while True:
            try:
                if time.time() - last_stat_update > 2:
                    self.ipc.set_state("engine_stats", {
                        "status": "OPTIMAL",
                        "msgs_rx": self.server.stats["msgs_rx"],
                        "msgs_tx": self.server.stats["msgs_tx"],
                        "latency": self.server.stats["last_latency"],
                        "active_clients": len(self.server.clients),
                        "uptime": time.time()
                    })
                    last_stat_update = time.time()

                messages = self.ipc.xread({"stream:orchestrator": '0'}, count=10, block=1)
                if messages:
                    for stream, msgs in messages:
                        for msg_id, data in msgs:
                            event = json.loads(data[b'payload']); e_type = event.get("type")
                            if e_type == "MARKET_DATA":
                                self.ipc.xadd("stream:Meta_1", {"payload": json.dumps({"type": "MARKET_DATA_REFRESH", "symbol": event["symbol"]})}, maxlen=100)
                                for b in ["Indicator_1", "Indicator_2", "Indicator_3", "Trend_1", "Trend_2", "Liquidity_1", "Regime_1", "Anomaly_1"]:
                                    self.ipc.xadd(f"stream:{b}", {"payload": json.dumps(event)}, maxlen=100)
                                self.ipc.xadd("stream:NewsRisk_1", {"payload": json.dumps(event)}, maxlen=100)
                            elif e_type in ["EVIDENCE", "REGIME_STATUS", "VETO", "NEWS_VETO", "ANOMALY_STATUS"]:
                                self.ipc.xadd("stream:Meta_1", {"payload": json.dumps(event)}, maxlen=1000)
                            elif e_type == "PROBABILISTIC_SIGNAL":
                                self.ipc.xadd("stream:Contrarian_1", {"payload": json.dumps(event)}, maxlen=1000)
                                self.ipc.xadd(f"stream:Risk_{1 if counter % 2 == 0 else 2}", {"payload": json.dumps(event)}, maxlen=1000)
                                counter += 1
                            elif e_type == "VALIDATED_TRADE":
                                self.ipc.xadd(f"stream:Execution_{1 if counter % 2 == 0 else 2}", {"payload": json.dumps(event)}, maxlen=1000)
                                counter += 1
                            elif e_type == "EXECUTION_ORDER":
                                self.ipc.xadd("stream:Memory_1", {"payload": json.dumps(event)}, maxlen=1000)
                                asyncio.create_task(self.server.broadcast(event))
                            elif e_type == "RELIABILITY_REPORT":
                                self.ipc.xadd("stream:Meta_1", {"payload": json.dumps(event)}, maxlen=100)
                            elif e_type == "EMERGENCY_KILL":
                                logger.critical("EMERGENCY KILL RECEIVED FROM DASHBOARD")
                                self.stop()
                                return
                            self.ipc.xdel("stream:orchestrator", msg_id)
                else:
                    await asyncio.sleep(0.001)
            except Exception as e:
                logger.error(f"Orchestrator Loop Error: {e}"); await asyncio.sleep(0.1)

    def stop(self):
        self.registry.stop_all()
        if self.native_dash.is_alive(): self.native_dash.terminate()
        if self.web_dash.is_alive(): self.web_dash.terminate()
