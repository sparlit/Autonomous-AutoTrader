import asyncio
import logging
import multiprocessing
import os
import signal
import sys
import psutil
import time
import ujson as json
import pandas as pd
from typing import Dict, Any, List, Optional
from src.python.hive.ipc import HiveIPC
from src.python.bridge.dashboards.native_gui import NativeDashboard
from src.python.bridge.dashboards.web_server import WebDashboard
from src.python.bridge.watchdog import L99Watchdog
from src.python.bridge.server import BridgeServer
from src.python.hive.config import AATConfig, load_config
from src.python.analyst.price_action import SMCAnalyst
from src.python.brains.registry import BrainRegistry

# Strategy Brains
from src.python.brains.strategies.swing_master import SwingMaster
from src.python.brains.strategies.scalp_master import ScalpMaster
from src.python.brains.strategies.vsa_master import VSAMaster
from src.python.brains.strategies.wyckoff_master import WyckoffMaster
from src.python.brains.strategies.ict_killzone import ICTKillzone
from src.python.brains.consensus import MetaBrain

# Specialized / Analyst Brains
from src.python.brains.specialized import (
    MarketDataBrain, TrendBrain, IndicatorBrain, LiquidityBrain, RegimeBrain,
    ContrarianBrain, NewsRiskBrain, MemoryBrain, RiskBrain,
    ExecutionBrain, AnomalyBrain, PortfolioBrain, CorrelationBrain,
    MomentumBrain, StructureBrain, MonitoringBrain
)

# Execution Managers
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager
from src.python.execution.manager import PositionManager

logger = logging.getLogger("AAT_Supervisor")

class HiveOrchestrator:
    """
    10001: The Supervisor (Process 0).
    Responsible for the 23-brain process lifecycle and dynamic affinity mapping.
    """
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        self.config = load_config()
        self.credentials = credentials
        self.ipc = HiveIPC()
        self.registry = BrainRegistry()

        # Core Components
        self.server = BridgeServer(self.config.bridge.host, self.config.bridge.port, self.handle_client_message)
        self.ledger = TradeLedger(self.config.system.database_path)
        self.risk_manager = RiskManager(self.config.risk)
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.watchdog = L99Watchdog(self)
        self.smc = SMCAnalyst()

        self.running = True
        self.brains = []

    async def run(self):
        """10002: Orchestration Entry Point."""
        logger.info("Initializing Phoenix Gauntlet V3.3.0...")

        # 1. Database and Shared Memory
        await self.ledger.init_db()
        self.ipc.clear_memory()

        # 2. Start Brains
        self._spawn_brain_swarm()

        # 3. Start Bridge Server
        asyncio.create_task(self.server.start())

        # 4. Start Watchdog
        asyncio.create_task(self.watchdog.run())

        logger.info("AAT V3.3.0 Fully Operational.")

        # 5. Main Orchestration Loop
        await self._orchestration_loop()

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """10010: Inbound message router for MT5 Clients."""
        m_type = message.get("t")

        if m_type == "HB": # Heartbeat
            self.watchdog.heartbeat()
            self.ipc.set_state("account_stats", {
                "equity": message.get("eq", 0.0),
                "drawdown": message.get("dd", 0.0),
                "pos_count": message.get("pc", 0),
                "spread": message.get("sp", 0.0),
                "candle_timer": message.get("ct", "--:--"),
                "last_hb": time.time()
            })
            # Also route to PortfolioBrain for VaR checks
            message["type"] = "HB"
            self.ipc.xadd("stream:Portfolio_1", message)
            return {"t": "ACK"}

        elif m_type == "MARKET_DATA":
            message["type"] = "MARKET_DATA"
            self.ipc.xadd("stream:orchestrator", message)
            return {"t": "ACK"}

        elif m_type == "DP":
            # Market data push
            message["type"] = "MARKET_DATA_RAW"
            self.ipc.xadd("stream:MarketData_1", message)
            return {"t": "ACK"}

        elif m_type == "SYNC":
            tickets = message.get("tickets", [])
            for t in tickets:
                await self.ledger.update_trade_from_sync(
                    t['tk'], t['s'], t['act'], t['vol'], t['sl'], t['tp']
                )
            return {"t": "SYNC_ACK"}

        return {"t": "ACK"}

    async def _orchestration_loop(self):
        """10012: The central event bus reader."""
        logger.info("Event Bus listener active.")
        while self.running:
            try:
                messages = self.ipc.xread({"stream:orchestrator": "0"}, count=50)
                if messages:
                    for stream, msgs in messages:
                        for msg_id, data in msgs:
                            event = json.loads(data[b'payload'])
                            await self._process_orchestrator_event(event)

                self._update_system_stats()
                await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"Orchestration Loop Error: {e}")
                await asyncio.sleep(0.1)

    async def _process_orchestrator_event(self, event: Dict[str, Any]):
        """10013: Logic for cross-component orchestration."""
        e_type = event.get("type")

        if e_type == "MARKET_DATA":
            # 10506: Compute live structure for Hybrid Trailing
            symbol = event.get("symbol")
            bid = event.get("bid", 0.0)
            ask = event.get("ask", 0.0)
            atr = event.get("atr", 0.0)
            ltf_df = pd.DataFrame(event.get("ltf", []))
            smc_data = None
            if not ltf_df.empty:
                if isinstance(event["ltf"][0], list):
                    ltf_df.columns = ["o", "h", "l", "c", "t", "v"]
                smc_data = self.smc.detect_market_structure(ltf_df, atr)

            orders = await self.pos_manager.monitor_and_manage(symbol, bid, ask, atr, smc_data=smc_data)
            for order in orders:
                order["magic"] = self.config.system.global_magic
                await self.server.broadcast(order)

            # Fan out to all listening Brains
            for stream in self.ipc._queues.keys():
                if stream.startswith("stream:") and stream != "stream:orchestrator":
                    self.ipc.xadd(stream, event)

        elif e_type == "EXECUTION_ORDER":
            # Final output from ExecutionBrain
            event["magic"] = self.config.system.global_magic
            if event.get("t") == "DEC":
                # Record intent and get internal ID
                internal_id = await self.ledger.record_intent(
                    event["s"], event["act"], event["lts"], event["sl_p"], event["tp_p"]
                )
                event["id"] = internal_id
            await self.server.broadcast(event)

        elif e_type == "TELEMETRY":
            telemetry_msg = {
                "t": "TLM",
                "s": event["symbol"],
                "st": "OPTIMAL" if self.server.clients else "WAITING",
                "scr": event["scr"],
                "htf": event["htf"],
                "dd": self.ipc.get_state("account_stats", {}).get("drawdown", 0.0),
                "pc": self.ipc.get_state("account_stats", {}).get("pos_count", 0)
            }
            await self.server.broadcast(telemetry_msg)

        elif e_type in ["RELIABILITY_REPORT", "VETO", "NEWS_VETO"]:
            # Route to MetaBrain
            self.ipc.xadd("stream:MetaBrain", event)

    def _update_system_stats(self):
        stats = {
            "status": "OPTIMAL" if self.server.clients else "WAITING",
            "active_clients": len(self.server.clients),
            "msgs_rx": self.server.stats["msgs_rx"],
            "msgs_tx": self.server.stats["msgs_tx"],
            "latency": self.server.stats["last_latency"],
            "server_time": time.time()
        }
        self.ipc.set_state("engine_stats", stats)
        # Periodic update of active trades for dashboards
        asyncio.create_task(self._sync_trades_to_ipc())

    async def _sync_trades_to_ipc(self):
        trades = await self.ledger.get_all_active_trades()
        self.ipc.set_state("active_trades", trades)

    async def broadcast_command(self, cmd: Dict[str, Any]):
        """Publish command to all connected clients."""
        await self.server.broadcast(cmd)

    def _spawn_brain_swarm(self):
        """10015: Parallel process spawning with affinity locking."""
        swarm = [
            (MarketDataBrain, "MarketData_1"),
            (TrendBrain, "Trend_1"),
            (IndicatorBrain, "Indicator_1"),
            (MomentumBrain, "Momentum_1"),
            (StructureBrain, "Structure_1"),
            (LiquidityBrain, "Liquidity_1"),
            (RegimeBrain, "Regime_1"),
            (ContrarianBrain, "Contrarian_1"),
            (NewsRiskBrain, "NewsRisk_1"),
            (MemoryBrain, "Memory_1"),
            (RiskBrain, "Risk_1"),
            (ExecutionBrain, "Execution_1"),
            (AnomalyBrain, "Anomaly_1"),
            (PortfolioBrain, "Portfolio_1"),
            (CorrelationBrain, "Correlation_1"),
            (MonitoringBrain, "Monitoring_1"),
            (SwingMaster, "SwingMaster"),
            (ScalpMaster, "ScalpMaster"),
            (VSAMaster, "VSAMaster"),
            (WyckoffMaster, "WyckoffMaster"),
            (ICTKillzone, "ICTKillzone"),
            (MetaBrain, "MetaBrain")
        ]

        for i, (brain_cls, name) in enumerate(swarm):
            cpu_cores = [i % psutil.cpu_count()]
            brain = brain_cls(name=name, ipc=self.ipc)
            self.registry.register(brain)

        self.registry.start_all()
        self.brains = list(self.registry._brains.values())

    def stop(self, *args):
        self.running = False
        self.registry.stop_all()
        logger.info("AAT V3.3.0 Shutdown Complete.")
