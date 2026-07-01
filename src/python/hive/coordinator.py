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
from src.python.hive.hardware_analyst import HardwareAnalyst

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
        self.hardware = HardwareAnalyst(self.config.system.database_path)

        # Core Components
        self.server = BridgeServer(self.config.bridge.host, self.config.bridge.port, self.handle_client_message)
        self.ledger = TradeLedger(self.config.system.database_path)
        # Pass IPC to RiskManager for shared state
        self.risk_manager = RiskManager(self.config, ipc=self.ipc)
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.watchdog = L99Watchdog(self)
        self.smc = SMCAnalyst()

        self.running = True
        self.brains = []

    async def run(self):
        """10002: Orchestration Entry Point."""
        logger.info("Initializing Phoenix Gauntlet V3.3.0...")
        self.hardware.log_capabilities()

        # 1. Database and Shared Memory
        await self.ledger.init_db()
        self.ipc.clear_memory()

        # Pre-initialize MUST-HAVE streams
        self.ipc.create_stream("stream:orchestrator")

        # 2. Start Brains
        await self._spawn_brain_swarm()

        # 3. Start Bridge Server
        asyncio.create_task(self.server.start())

        # 4. Start Watchdog
        asyncio.create_task(self.watchdog.run())

        # 10450: Launch Monitoring Dashboards
        self.web_dash = WebDashboard(ipc=self.ipc, port=self.config.bridge.dashboard_port)
        self.web_dash.start()

        self.native_dash = NativeDashboard(ipc=self.ipc)
        self.native_dash.start()

        logger.info("AAT V3.3.0 Fully Operational.")

        # Pin orchestrator to Core 1 if available
        self._setup_affinity()

        # 5. Main Orchestration Loop
        await self._orchestration_loop()

    def _setup_affinity(self):
        try:
            p = psutil.Process(os.getpid())
            if psutil.cpu_count() > 1:
                p.cpu_affinity([1])
                logger.info("Orchestrator pinned to CPU 1")
        except Exception as e:
            logger.debug(f"Orchestrator affinity fail: {e}")

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """10010: Inbound message router for MT5 Clients."""
        m_type = message.get("t")

        if m_type == "HB": # Heartbeat
            self.watchdog.heartbeat()
            equity = message.get("eq", message.get("e", 0.0))

            # 10025: Global peak tracking for drawdown enforcement
            if equity > self.risk_manager.peak_equity:
                self.risk_manager.peak_equity = equity

            self.ipc.set_state("account_stats", {
                "equity": equity,
                "drawdown": message.get("dd", message.get("d", 0.0)),
                "pos_count": message.get("pc", 0),
                "spread": message.get("sp", 0.0),
                "candle_timer": message.get("ct", "--:--"),
                "last_hb": time.time()
            })
            self.ipc.xadd("stream:Portfolio_1", {"type": "HB", **message})
            return {"t": "ACK"}

        elif m_type == "DP": # Data Push
            message["type"] = "MARKET_DATA_RAW"
            self.ipc.xadd("stream:MarketData_1", message)
            return {"t": "ACK"}

        elif m_type == "SYNC":
            tickets = message.get("tk", [])
            for t in tickets:
                await self.ledger.update_trade_from_sync(
                    t['tk'], t['s'], t['act'], t['vol'], t['sl'], t['tp']
                )
            # Prune closed trades
            active_tickets = [t["tk"] for t in tickets]
            await self.ledger.prune_trades(active_tickets)
            return {"t": "SYNC_ACK"}

        return {"t": "SYNC_REQ"}

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
                    await asyncio.sleep(0.005)
                else:
                    await asyncio.sleep(0.02)

                self._update_system_stats()
            except Exception as e:
                logger.error(f"Orchestration Loop Error: {e}")
                await asyncio.sleep(0.1)

    async def _process_orchestrator_event(self, event: Dict[str, Any]):
        """10013: Institutional Event Routing."""
        e_type = event.get("type")

        if e_type == "MARKET_DATA":
            # 1. Run Position Management (Trailing SL, etc)
            symbol = event.get("symbol")
            bid, ask, atr = event.get("bid", 0), event.get("ask", 0), event.get("atr", 0)
            ltf_df = pd.DataFrame(event.get("ltf", []))
            smc_data = None
            if not ltf_df.empty:
                if isinstance(event["ltf"][0], list): ltf_df.columns = ["o", "h", "l", "c", "t", "v"]
                smc_data = self.smc.detect_market_structure(ltf_df, atr)

            orders = await self.pos_manager.monitor_and_manage(symbol, bid, ask, atr, smc_data=smc_data)
            for order in orders:
                order["magic"] = self.config.system.global_magic
                await self.server.broadcast(order)

            # 2. Fan out to Strategy/Analyst Brains
            strategy_swarm = [
                "Trend_1", "Indicator_1", "Momentum_1", "Structure_1", "Liquidity_1",
                "Regime_1", "Anomaly_1", "SwingMaster", "ScalpMaster",
                "VSAMaster", "WyckoffMaster", "ICTKillzone"
            ]
            for b in strategy_swarm:
                self.ipc.xadd(f"stream:{b}", event)

        elif e_type in ["EVIDENCE", "REGIME_STATUS", "MOMENTUM_STATUS", "STRUCTURE_STATUS"]:
            self.ipc.xadd("stream:MetaBrain", event)

        elif e_type == "PROBABILISTIC_SIGNAL":
            for b in ["Risk_1", "Contrarian_1", "Correlation_1", "NewsRisk_1"]:
                self.ipc.xadd(f"stream:{b}", event)

        elif e_type in ["VETO", "NEWS_VETO"]:
            self.ipc.xadd("stream:MetaBrain", event)
            self.ipc.xadd("stream:Risk_1", event)

        elif e_type == "VALIDATED_TRADE":
            # Route to Actuator
            self.ipc.xadd("stream:Execution_1", event)

        elif e_type == "EXECUTION_ORDER":
            # Final output to MT5
            event["magic"] = self.config.system.global_magic
            if event.get("t") == "DEC":
                internal_id = await self.ledger.record_intent(
                    event["s"], event["act"], event["lts"], event["sl_p"], event["tp_p"]
                )
                event["id"] = internal_id
                # 10020: Increment shared trade count globally
                self.risk_manager.increment_trade_count(event["s"])

            await self.server.broadcast(event)

        elif e_type == "TELEMETRY":
            telemetry_msg = {
                "t": "TLM", "s": event["symbol"], "st": "OPTIMAL" if self.server.clients else "WAITING",
                "scr": event["scr"], "htf": event["htf"],
                "dd": self.ipc.get_state("account_stats", {}).get("drawdown", 0.0),
                "pc": self.ipc.get_state("account_stats", {}).get("pos_count", 0)
            }
            await self.server.broadcast(telemetry_msg)

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
        asyncio.create_task(self._sync_trades_to_ipc())

    async def _sync_trades_to_ipc(self):
        trades = await self.ledger.get_all_active_trades()
        now = time.time()
        enriched_trades = []
        for t in trades:
            symbol = t['symbol']
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            bid = s_stats.get("bid", 0)
            ask = s_stats.get("ask", 0)
            tick_val = s_stats.get("tick_val", 10.0)
            tick_size = s_stats.get("tick_size", 0.0001)

            if bid > 0 and ask > 0:
                current_price = bid if t['action'] == "BUY" else ask
                diff = (current_price - t['entry_price']) if t['action'] == "BUY" else (t['entry_price'] - current_price)
                t['pl_points'] = diff / tick_size if tick_size > 0 else 0
                t['pl_currency'] = t['lots'] * t['pl_points'] * tick_val if tick_size > 0 else 0
            else:
                t['pl_points'] = 0.0
                t['pl_currency'] = 0.0

            t['duration'] = now - t['timestamp']
            if t.get('partial_tp_hit') == 1:
                t['status'] = "PARTIAL_HIT"

            enriched_trades.append(t)

        self.ipc.set_state("active_trades", enriched_trades)

    async def broadcast_command(self, cmd: Dict[str, Any]):
        await self.server.broadcast(cmd)

    async def _spawn_brain_swarm(self):
        """10015: Stabilized parallel process spawning."""
        swarm_classes = [
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

        for _, name in swarm_classes:
            self.ipc.create_stream(f"stream:{name}")

        affinity_map = self.hardware.get_optimized_affinity_map(len(swarm_classes))

        for i, (brain_cls, name) in enumerate(swarm_classes):
            if name in ["MetaBrain", "Trend_1", "Indicator_1", "MarketData_1"]:
                 brain = brain_cls(name=name, ipc=self.ipc, cpu_affinity=affinity_map.get(i))
            else:
                 brain = brain_cls(name=name, ipc=self.ipc)
                 brain.cpu_affinity = affinity_map.get(i)

            self.registry.register(brain)
            brain.start()
            await asyncio.sleep(0.1)

        self.brains = list(self.registry._brains.values())

    def stop(self, *args):
        self.running = False
        if hasattr(self, 'web_dash'): self.web_dash.terminate()
        if hasattr(self, 'native_dash'): self.native_dash.terminate()
        self.registry.stop_all()
        logger.info("AAT V3.3.0 Shutdown Complete.")
