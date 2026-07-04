import asyncio
import logging
import time
import ujson as json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.python.hive.ipc import HiveIPC
from src.python.brains.registry import BrainRegistry
from src.python.hive.hardware_analyst import HardwareAnalyst
from src.python.bridge.server import BridgeServer
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager
from src.python.execution.manager import PositionManager
from src.python.analyst.price_action import SMCAnalyst
from src.python.brains.specialized import *
from src.python.brains.consensus import MetaBrain
from src.python.hive.config import load_config

logger = logging.getLogger("AAT_HiveOrchestrator")

class HiveOrchestrator:
    """V4.0-PRO: Hardened Institutional Execution Orchestrator."""
    def __init__(self, credentials=None):
        self.config = load_config()
        self.ipc = HiveIPC()
        self.registry = BrainRegistry()
        self.hardware = HardwareAnalyst()
        self.server = BridgeServer(host=self.config.bridge.host, port=self.config.bridge.port, on_message_cb=self.handle_bridge_message)
        self.ledger = TradeLedger(db_path=self.config.system.database_path)
        self.risk_manager = RiskManager(self.config, ipc=self.ipc)
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.running = True
        self.start_time = time.time()
        self._msg_counts = 0

    async def run(self):
        logger.info("🌌 AAT V4.0-PRO Phoenix Core Online.")
        await self.ledger.init_db()
        self.ipc.clear_memory()
        self.ipc.set_state("institutional_settings", self.config.institutional.dict())
        await self.server.start()
        await self._spawn_brain_swarm()
        await self._orchestration_loop()

    async def handle_bridge_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        m_type = message.get("t")
        if m_type == "HB":
            self.ipc.set_state("account_stats", {
                "equity": float(message.get("eq", 0)),
                "balance": float(message.get("ba", 0)),
                "drawdown": float(message.get("dd", 0)),
                "pos_count": int(message.get("pc", 0)),
                "ts": time.time()
            })
            return {"t": "HB_ACK", "lot": self.config.institutional.standard_lot_size, "v": self.config.institutional.version}

        elif m_type == "DP":
            # Rule 1: High-throughput Data Injection
            symbol = message.get("s")
            bid = float(message.get("bi", 0))
            ask = float(message.get("as", 0))
            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask, "tick_val": float(message.get("tv", 10.0)),
                "tick_size": float(message.get("ts", 0.0001)), "atr": float(message.get("atr", 0))
            })
            event = {
                "type": "MARKET_DATA", "symbol": symbol, "bid": bid, "ask": ask,
                "atr": float(message.get("atr", 0)), "ltf": message.get("ltf", []), "mtf": message.get("mtf", {})
            }
            self.ipc.xadd("stream:orchestrator", event)
            return {"t": "ACK"}

        elif m_type == "T_ACK":
            await self.ledger.confirm_trade(int(message.get("id")), int(message.get("tk")), 0, 0, 0)
            return {"t": "ACK"}

        elif m_type == "SYNC":
            tickets = message.get("tk", [])
            for t in tickets:
                await self.ledger.update_trade_from_sync(t['tk'], t['s'], t['act'], t['vol'], float(t['en']), float(t['sl']), float(t['tp']))
            await self.ledger.prune_trades([t["tk"] for t in tickets])
            return {"t": "SYNC_ACK"}

        return {"t": "SYNC_REQ"}

    async def _orchestration_loop(self):
        while self.running:
            try:
                messages = self.ipc.xread({"stream:orchestrator": "0"}, count=50)
                if messages:
                    tasks = []
                    for _, msgs in messages:
                        for _, data in msgs:
                            self._msg_counts += 1
                            tasks.append(self._process_orchestrator_event(json.loads(data[b'payload'])))
                    if tasks: await asyncio.gather(*tasks)
                    await asyncio.sleep(0.001)
                else: await asyncio.sleep(0.01)
                self._update_system_stats()
            except Exception as e:
                logger.error(f"Core Error: {e}")
                await asyncio.sleep(0.1)

    async def _process_orchestrator_event(self, event: Dict[str, Any]):
        e_type = event.get("type")
        symbol = event.get("symbol")

        if e_type == "MARKET_DATA":
            # 1. Parallel Analysis
            for b in ["Trend_1", "Indicator_1"]: self.ipc.xadd(f"stream:{b}", event)

            # 2. Sequential Position Management (Rule 1.c/1.d)
            orders = await self.pos_manager.monitor_and_manage(symbol, event["bid"], event["ask"], event["atr"], mtf_trends=self.ipc.get_state(f"trend_stats:{symbol}"))
            for o in orders:
                if o.get("type") == "PROBABILISTIC_SIGNAL": self.ipc.xadd("stream:orchestrator", o)
                else: await self.server.broadcast(o)

        elif e_type == "EVIDENCE":
            self.ipc.xadd("stream:MetaBrain", event)

        elif e_type == "PROBABILISTIC_SIGNAL":
            # Rule 1.b/1.c assessment pipeline
            self.ipc.xadd("stream:Risk_1", event)

        elif e_type == "VALIDATED_TRADE":
            # Rule 1.a: Duplicate Check
            active = await self.ledger.get_active_trades_db(symbol)
            if any(t['action'] == event['action'] for t in active) and not event.get("scaling"):
                logger.warning(f"Duplicate trade blocked for {symbol}")
                return
            self.ipc.xadd("stream:Execution_1", event)

        elif e_type == "EXECUTION_ORDER":
            event["magic"] = self.config.system.global_magic
            if event.get("t") == "DEC":
                event["id"] = await self.ledger.record_intent(event["s"], event["act"], event["lts"], int(event["sl_p"]), int(event["tp_p"]))
                self.risk_manager.increment_trade_count(event["s"])
            await self.server.broadcast(event)

    def _update_system_stats(self):
        stats = {"status": "V4.0-PRO_OPTIMAL" if self.server.clients else "WAITING", "active_clients": len(self.server.clients),
                 "throughput": float(self._msg_counts / (time.time() - self.start_time)), "server_time": time.time()}
        self.ipc.set_state("engine_stats", stats)
        asyncio.create_task(self._sync_trades_to_ipc())

    async def _sync_trades_to_ipc(self):
        trades = await self.ledger.get_all_active_trades()
        self.ipc.set_state("active_trades", trades)

    async def _spawn_brain_swarm(self):
        swarm = [(MarketDataBrain, "MarketData_1"), (TrendBrain, "Trend_1"), (IndicatorBrain, "Indicator_1"),
                 (RiskBrain, "Risk_1"), (ExecutionBrain, "Execution_1"), (MetaBrain, "MetaBrain")]
        for _, name in swarm: self.ipc.create_stream(f"stream:{name}")
        for i, (brain_cls, name) in enumerate(swarm):
            brain = brain_cls(name=name, ipc=self.ipc)
            self.registry.register(brain)
            brain.start()
            await asyncio.sleep(0.05)

    def stop(self, *args):
        self.running = False
        self.registry.stop_all()
        logger.info("AAT V4.0-PRO Shutdown Complete.")
