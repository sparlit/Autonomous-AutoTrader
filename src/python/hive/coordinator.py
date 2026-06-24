import asyncio
import ujson as json
import logging
import time
import os
import psutil
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
        self._initialize_brains()
        self._initialize_ipc_queues()
        self._initialize_dashboards()

        self.ipc.set_state("account_stats", {"equity": 0.0, "drawdown": 0.0, "pos_count": 0})
        self.ipc.set_state("engine_stats", {"status": "STARTING", "msgs_rx": 0, "msgs_tx": 0, "latency": 0.0, "active_clients": 0, "mps": 0.0, "server_time": time.time()})

    def _initialize_brains(self):
        # 23 Specialized Brains (some redundant instances for load balancing)
        self.registry.register(MarketDataBrain("MarketData_1", cpu_affinity=[2], ipc=self.ipc))
        self.registry.register(MarketDataBrain("MarketData_2", cpu_affinity=[3], ipc=self.ipc))

        # CPU 4-6: Indicators (Fast, MTF)
        self.registry.register(IndicatorBrain("Indicator_1", cpu_affinity=[4], ipc=self.ipc)) # M1
        self.registry.register(IndicatorBrain("Indicator_2", cpu_affinity=[5], ipc=self.ipc)) # M5
        self.registry.register(IndicatorBrain("Indicator_3", cpu_affinity=[6], ipc=self.ipc)) # H1

        # CPU 7-8: Trend (MTF Alignment)
        self.registry.register(TrendBrain("Trend_1", cpu_affinity=[7], ipc=self.ipc))
        self.registry.register(TrendBrain("Trend_2", cpu_affinity=[8], ipc=self.ipc))

        # CPU 9: Liquidity (SMC OB)
        self.registry.register(LiquidityBrain("Liquidity_1", cpu_affinity=[9], ipc=self.ipc))
        self.registry.register(MomentumBrain("Momentum_1", cpu_affinity=[10], ipc=self.ipc))
        self.registry.register(RegimeBrain("Regime_1", cpu_affinity=[11], ipc=self.ipc))
        self.registry.register(MetaBrain("Meta_1", cpu_affinity=[12], threshold=self.config.brains.consensus_threshold, ipc=self.ipc))
        self.registry.register(NewsRiskBrain("NewsRisk_1", cpu_affinity=[13], ipc=self.ipc))
        self.registry.register(ContrarianBrain("Contrarian_1", cpu_affinity=[13], ipc=self.ipc))
        self.registry.register(CorrelationBrain("Correlation_1", cpu_affinity=[14], ipc=self.ipc))
        self.registry.register(RiskBrain("Risk_1", cpu_affinity=[15], ipc=self.ipc))
        self.registry.register(RiskBrain("Risk_2", cpu_affinity=[16], ipc=self.ipc))
        self.registry.register(ExecutionBrain("Execution_1", cpu_affinity=[17], ipc=self.ipc))
        self.registry.register(ExecutionBrain("Execution_2", cpu_affinity=[18], ipc=self.ipc))
        self.registry.register(MemoryBrain("Memory_1", cpu_affinity=[19], ipc=self.ipc))
        self.registry.register(MonitoringBrain("Monitoring_1", cpu_affinity=[19], ipc=self.ipc))
        self.registry.register(AnomalyBrain("Anomaly_1", cpu_affinity=[19], ipc=self.ipc))
        self.registry.register(PortfolioBrain("Portfolio_1", cpu_affinity=[19], ipc=self.ipc))
        self.registry.register(StructureBrain("Structure_1", cpu_affinity=[19], ipc=self.ipc))

    def _initialize_ipc_queues(self):
        queues = [
            "stream:orchestrator", "stream:MarketData_1", "stream:MarketData_2",
            "stream:Indicator_1", "stream:Indicator_2", "stream:Indicator_3",
            "stream:Trend_1", "stream:Trend_2", "stream:Liquidity_1", "stream:Momentum_1",
            "stream:Regime_1", "stream:Meta_1", "stream:Contrarian_1", "stream:NewsRisk_1",
            "stream:Correlation_1", "stream:Risk_1", "stream:Risk_2", "stream:Execution_1", "stream:Execution_2",
            "stream:Memory_1", "stream:Monitoring_1", "stream:Anomaly_1", "stream:Portfolio_1", "stream:Structure_1"
        ]
        for q in queues:
            self.ipc.get_queue(q)

    def _initialize_dashboards(self):
        self.native_dash = NativeDashboard(ipc=self.ipc)
        self.web_dash = WebDashboard(ipc=self.ipc, port=8009)

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "HB":
            symbol = message.get("s", "GLOBAL")
            self.ipc.set_state("account_stats", {
                "equity": message.get("e", 0.0), "drawdown": message.get("d", 0.0),
                "pos_count": message.get("pc", 0), "last_update": time.time()
            })
            # Merge with existing symbol stats to prevent overwritingscr/htf
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {"symbol": symbol, "scr": 0.5, "htf": "NEUTRAL"})
            s_stats.update({
                "spread": message.get("sp", 0.0),
                "candle_timer": message.get("ct", "--:--"),
                "last_update": time.time()
            })
            self.ipc.set_state(f"symbol_stats:{symbol}", s_stats)

        target = f"stream:MarketData_{1 if time.time() % 2 < 1 else 2}"
        self.ipc.xadd(target, {"payload": json.dumps(message)}, maxlen=1000)
        return {"t": "ACK"}

    async def run(self):
        p = psutil.Process(os.getpid())
        try: p.cpu_affinity([1])
        except: pass
        logger.info("Starting Dashboards...")
        self.native_dash.start(); self.web_dash.start()
        logger.info("Launching Brain Cluster...")
        self.registry.start_all()
        logger.info("Starting Bridge Server...")
        asyncio.create_task(self.server.start())
        await self._main_orchestration_loop()

    async def _main_orchestration_loop(self):
        counter = 0; last_stat_update = 0; last_rx = 0
        logger.info("Orchestration Loop Active.")
        while True:
            try:
                now = time.time()
                if now - last_stat_update >= 0.5:
                    current_rx = self.server.stats["msgs_rx"]
                    mps = (current_rx - last_rx) / (now - last_stat_update) if last_stat_update > 0 else 0
                    self.ipc.set_state("engine_stats", {
                        "status": "OPTIMAL", "msgs_rx": current_rx,
                        "msgs_tx": self.server.stats["msgs_tx"], "latency": self.server.stats["last_latency"],
                        "active_clients": len(self.server.clients), "uptime": now, "mps": mps,
                        "server_time": now
                    })
                    last_stat_update = now; last_rx = current_rx

                # Optimized: Read from stream once per loop
                messages = self.ipc.xread({"stream:orchestrator": '0'}, count=50, block=1)
                if messages:
                    for stream, msgs in messages:
                        for msg_id, data in msgs:
                            event = json.loads(data[b'payload'])
                            e_type = event.get("type")

                            if e_type == "MARKET_DATA":
                                self.ipc.xadd("stream:Meta_1", {"payload": json.dumps({"type": "MARKET_DATA_REFRESH", "symbol": event["symbol"]})}, maxlen=100)
                                for b in ["Indicator_1", "Indicator_2", "Indicator_3", "Trend_1", "Trend_2", "Liquidity_1", "Regime_1", "Anomaly_1", "Momentum_1", "Structure_1"]:
                                    self.ipc.xadd(f"stream:{b}", {"payload": json.dumps(event)}, maxlen=100)
                                self.ipc.xadd("stream:NewsRisk_1", {"payload": json.dumps(event)}, maxlen=100)
                            elif e_type in ["EVIDENCE", "REGIME_STATUS", "MOMENTUM_STATUS", "STRUCTURE_STATUS", "VETO", "NEWS_VETO", "ANOMALY_STATUS"]:
                                self.ipc.xadd("stream:Meta_1", {"payload": json.dumps(event)}, maxlen=1000)
                            elif e_type == "PROBABILISTIC_SIGNAL":
                                self.ipc.xadd("stream:Correlation_1", {"payload": json.dumps(event)}, maxlen=100)
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
                            elif e_type == "TELEMETRY":
                                sym = event["symbol"]
                                s_state = self.ipc.get_state(f"symbol_stats:{sym}", {"symbol": sym, "spread": 0.0, "candle_timer": "--:--"})
                                s_state.update({"scr": event["scr"], "htf": event["htf"], "last_update": time.time()})
                                self.ipc.set_state(f"symbol_stats:{sym}", s_state)

                                telemetry_msg = {"t": "TLM", "s": sym, "st": "OPTIMAL", "scr": event["scr"], "htf": event["htf"], "dd": event.get("dd", 0.0), "pc": self.ipc.get_state("account_stats", {}).get("pos_count", 0)}
                                asyncio.create_task(self.server.broadcast(telemetry_msg))
                            elif e_type == "EMERGENCY_KILL":
                                logger.warning("EMERGENCY KILL RECEIVED")
                                self.stop(); return
                            self.ipc.xdel("stream:orchestrator", msg_id)
                else:
                    # Use a slightly longer sleep if no messages to yield CPU
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"Orchestrator Loop Error: {e}"); await asyncio.sleep(0.1)

    def stop(self):
        logger.info("Stopping Orchestrator...")
        self.registry.stop_all()
        if hasattr(self, 'native_dash') and self.native_dash.is_alive(): self.native_dash.terminate()
        if hasattr(self, 'web_dash') and self.web_dash.is_alive(): self.web_dash.terminate()
