import asyncio
import ujson as json
import logging
import time
import psutil
import os
import pandas as pd
from typing import Dict, Any, List, Optional

from src.python.bridge.server import BridgeServer
from src.python.bridge.dashboards.native_gui import NativeDashboard
from src.python.bridge.dashboards.web_server import WebDashboard
from src.python.hive.ipc import HiveIPC
from src.python.hive.config import AATConfig, load_config
from src.python.hive.hardware_analyst import HardwareAnalyst
from src.python.brains.registry import BrainRegistry
from src.python.brains.specialized import (
    MarketDataBrain, IndicatorBrain, TrendBrain, MomentumBrain,
    LiquidityBrain, RegimeBrain, NewsRiskBrain, ContrarianBrain,
    CorrelationBrain, RiskBrain, ExecutionBrain, MemoryBrain,
    MonitoringBrain, AnomalyBrain, PortfolioBrain, StructureBrain
)
from src.python.brains.consensus import MetaBrain
from src.python.analyst.price_action import SMCAnalyst
from src.python.execution.ledger import TradeLedger
from src.python.execution.manager import PositionManager
from src.python.execution.risk_manager import RiskManager
from src.python.brains.strategies import STRATEGY_MAP
from src.python.analyst.normalization import AssetNormalizationLayer
from src.python.bridge.watchdog import L99Watchdog

logger = logging.getLogger("AAT_Orchestrator")

class HiveOrchestrator:
    def __init__(self, config_path: str = "config/main_config.json", credentials: Optional[Dict[str, str]] = None):
        self.config = load_config(config_path)
        self.credentials = credentials
        self.ipc = HiveIPC()
        self.hardware = HardwareAnalyst(db_path=self.config.system.database_path)
        self.server = BridgeServer(self.config.bridge.host, self.config.bridge.port, self.handle_client_message)
        self.registry = BrainRegistry()
        self.ledger = TradeLedger(db_path=self.config.system.database_path)
        self.risk_manager = RiskManager(self.config.risk)
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.smc = SMCAnalyst()
        self.normalization = AssetNormalizationLayer()
        self.global_magic = self.config.system.global_magic
        self._initialize_ipc_queues()
        self._initialize_brains()
        self._initialize_dashboards()
        self.watchdog = L99Watchdog(self.ipc, timeout=self.config.bridge.timeout)

    def _initialize_brains(self):
        core = [MarketDataBrain("MarketData_1", ipc=self.ipc), MarketDataBrain("MarketData_2", ipc=self.ipc), IndicatorBrain("Indicator_1", ipc=self.ipc), IndicatorBrain("Indicator_2", ipc=self.ipc), IndicatorBrain("Indicator_3", ipc=self.ipc), TrendBrain("Trend_1", ipc=self.ipc), TrendBrain("Trend_2", ipc=self.ipc), LiquidityBrain("Liquidity_1", ipc=self.ipc), MomentumBrain("Momentum_1", ipc=self.ipc), RegimeBrain("Regime_1", ipc=self.ipc), NewsRiskBrain("NewsRisk_1", ipc=self.ipc), ContrarianBrain("Contrarian_1", ipc=self.ipc), CorrelationBrain("Correlation_1", ipc=self.ipc), RiskBrain("Risk_1", ipc=self.ipc), RiskBrain("Risk_2", ipc=self.ipc), ExecutionBrain("Execution_1", ipc=self.ipc), ExecutionBrain("Execution_2", ipc=self.ipc), MemoryBrain("Memory_1", ipc=self.ipc), MonitoringBrain("Monitoring_1", ipc=self.ipc), AnomalyBrain("Anomaly_1", ipc=self.ipc), PortfolioBrain("Portfolio_1", ipc=self.ipc), StructureBrain("Structure_1", ipc=self.ipc)]
        strats = [cls(name, ipc=self.ipc) for name, cls in STRATEGY_MAP.items()]
        meta = MetaBrain("Meta_1", threshold=self.config.brains.consensus_threshold, ipc=self.ipc)
        meta.required_sources = list(STRATEGY_MAP.keys())
        all_b = core + strats + [meta]
        aff = self.hardware.get_optimized_affinity_map(len(all_b))
        for i, b in enumerate(all_b):
            b.cpu_affinity = aff.get(i, [0])
            self.registry.register(b)

    def _initialize_ipc_queues(self):
        qs = ["stream:orchestrator", "stream:MarketData_1", "stream:MarketData_2", "stream:Indicator_1", "stream:Indicator_2", "stream:Indicator_3", "stream:Trend_1", "stream:Trend_2", "stream:Liquidity_1", "stream:Momentum_1", "stream:Regime_1", "stream:Meta_1", "stream:Contrarian_1", "stream:NewsRisk_1", "stream:Correlation_1", "stream:Risk_1", "stream:Risk_2", "stream:Execution_1", "stream:Execution_2", "stream:Memory_1", "stream:Monitoring_1", "stream:Anomaly_1", "stream:Portfolio_1", "stream:Structure_1"]
        for s in STRATEGY_MAP.keys(): qs.append(f"stream:{s}")
        for q in qs: self.ipc.create_stream(q, maxlen=5000)

    def _initialize_dashboards(self):
        self.native_dash = NativeDashboard(ipc=self.ipc)
        self.web_dash = WebDashboard(ipc=self.ipc, port=self.config.bridge.dashboard_port)

    async def handle_client_message(self, cid, msg):
        m_type = msg.get("t")
        if m_type == "HB":
            raw_s = msg.get("s", "UNKNOWN"); symbol = self.normalization.normalize_symbol(raw_s)
            self.ipc.set_state("account_stats", {"equity": msg.get("e", 0.0), "drawdown": msg.get("d", 0.0), "pos_count": msg.get("pc", 0), "spread": msg.get("sp", 0.0), "candle_timer": msg.get("ct", "--:--"), "last_update": time.time()})
            self.ipc.set_state(f"symbol_stats:{symbol}", {"symbol": symbol, "spread": msg.get("sp", 0.0), "candle_timer": msg.get("ct", "--:--"), "last_update": time.time()})
        elif m_type == "SYNC":
            for t in msg.get("tk", []): await self.ledger.update_trade_from_sync(t["tk"], msg.get("s"), "BUY" if t["type"]==0 else "SELL", t["vol"], t["sl"], t["tp"])
        self.ipc.xadd(f"stream:MarketData_{1 if time.time() % 2 < 1 else 2}", msg, maxlen=1000)
        return {"t": "ACK"}

    async def trigger_emergency_safety(self):
        logger.critical("🚨 EMERGENCY")
        await self.server.broadcast({"t": "DEC", "mgmt": "CLOSE_ALL"})
        await self.ledger.close_all_active_trades()

    async def run(self):
        self.ipc.clear_memory()
        await self.ledger.init_db()
        self.native_dash.start(); self.web_dash.start()
        self.registry.start_all()
        asyncio.create_task(self.server.start())
        asyncio.create_task(self.watchdog.run(self))
        await self._main_orchestration_loop()

    async def _main_orchestration_loop(self):
        last_stat = 0
        while True:
            try:
                now = time.time()
                if now - last_stat >= 0.5:
                    self.ipc.set_state("engine_stats", {"status": "OPTIMAL" if self.server.clients else "WAITING", "active_clients": len(self.server.clients), "server_time": now})
                    self.ipc.set_state("active_trades", await self.ledger.get_all_active_trades())
                    last_stat = now
                messages = self.ipc.xread({"stream:orchestrator": '0'}, count=50, block=1)
                if messages:
                    for _, msgs in messages:
                        for mid, data in msgs:
                            event = json.loads(data[b'payload'])
                            et = event.get("type")
                            if et == "MARKET_DATA":
                                ltf = pd.DataFrame(event.get("ltf", []))
                                if not ltf.empty:
                                    if isinstance(event["ltf"][0], list): ltf.columns = ["o", "h", "l", "c", "t", "v"]
                                    smc = self.smc.detect_market_structure(ltf, event.get("atr", 0))
                                    for o in await self.pos_manager.monitor_and_manage(event["symbol"], event["bid"], event["ask"], event.get("atr", 0), smc_data=smc):
                                        o["magic"] = self.global_magic
                                        asyncio.create_task(self.server.broadcast(o))
                                    self.ipc.xadd("stream:Meta_1", {"payload": json.dumps({"type": "MARKET_DATA_REFRESH", "symbol": event["symbol"]})}, maxlen=100)
                                    for b in ["Indicator_1", "Indicator_2", "Indicator_3", "Trend_1", "Trend_2", "Liquidity_1", "Regime_1", "Anomaly_1", "Momentum_1", "Structure_1"]: self.ipc.xadd(f"stream:{b}", {"payload": json.dumps(event)}, maxlen=100)
                                    for s in STRATEGY_MAP.keys(): self.ipc.xadd(f"stream:{s}", {"payload": json.dumps(event)}, maxlen=100)
                                    self.ipc.xadd("stream:NewsRisk_1", {"payload": json.dumps(event)}, maxlen=100)
                            elif et == "EXECUTION_ORDER":
                                if event.get("t") == "DEC": event["id"] = await self.ledger.record_intent(event["s"], event["act"], event["lts"], event["sl_p"], event["tp_p"])
                                event["magic"] = self.global_magic
                                asyncio.create_task(self.server.broadcast(event))
                            elif et == "TELEMETRY":
                                asyncio.create_task(self.server.broadcast({"t": "TLM", "s": event["symbol"], "st": "OPTIMAL", "scr": event["scr"], "htf": event["htf"], "dd": 0.0, "pc": 0}))
                            self.ipc.xdel("stream:orchestrator", mid)
                else: await asyncio.sleep(0.01)
            except Exception as e: logger.error(f"Loop error: {e}"); await asyncio.sleep(0.1)

    def stop(self):
        self.registry.stop_all()
        if self.native_dash.is_alive(): self.native_dash.terminate()
        if self.web_dash.is_alive(): self.web_dash.terminate()
