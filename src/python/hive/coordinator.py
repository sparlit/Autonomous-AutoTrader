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
from src.python.bridge.watchdog import L99Watchdog
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager
from src.python.execution.manager import PositionManager
from src.python.analyst.price_action import SMCAnalyst
from src.python.brains.specialized import *
from src.python.brains.consensus import MetaBrain
from src.python.hive.config import load_config
from src.python.bridge.dashboards.native_gui import NativeDashboard
from src.python.bridge.dashboards.web_server import WebDashboard

logger = logging.getLogger("AAT_HiveOrchestrator")

class HiveOrchestrator:
    """V4.0-PRO: Hardened Institutional Execution Orchestrator."""
    def __init__(self, credentials=None):
        self.config = load_config()
        self.ipc = HiveIPC()
        self.registry = BrainRegistry()
        self.hardware = HardwareAnalyst()
        self.server = BridgeServer(host=self.config.bridge.host, port=self.config.bridge.port, on_message_cb=self.handle_bridge_message)
        self.watchdog = L99Watchdog(self, timeout=self.config.bridge.timeout)
        self.ledger = TradeLedger(db_path=self.config.system.database_path)
        self.risk_manager = RiskManager(self.config, ipc=self.ipc)
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.running = True
        self.start_time = time.time()
        self._msg_counts = 0
        self.native_dash = None
        self.web_dash = None
        self._background_tasks = set()
        self.brains = {}

    async def run(self):
        logger.info("🌌 AAT V4.0-PRO Phoenix Core Online.")
        await self.ledger.init_db()
        self.ipc.clear_memory()
        self.ipc.set_state("institutional_settings", self.config.institutional.dict())
        self.ipc.set_state("hardware_report", self.hardware.get_system_report())

        default_reliability = {
            "MarketData_1": 1.0, "Trend_1": 0.85, "Indicator_1": 0.80, "Regime_1": 1.0,
            "Risk_1": 1.0, "MetaBrain": 0.95, "Execution_1": 1.0
        }
        self.ipc.set_state("brain_reliability", default_reliability)

        self.native_dash = NativeDashboard(ipc=self.ipc)
        self.native_dash.start()

        self.web_dash = WebDashboard(ipc=self.ipc, port=self.config.bridge.dashboard_port)
        self.web_dash.start()

        bridge_task = asyncio.create_task(self.server.start())
        self._background_tasks.add(bridge_task)
        bridge_task.add_done_callback(self._background_tasks.discard)

        watchdog_task = asyncio.create_task(self.watchdog.run())
        self._background_tasks.add(watchdog_task)
        watchdog_task.add_done_callback(self._background_tasks.discard)

        await self._spawn_brain_swarm()
        await self._orchestration_loop()

    async def handle_bridge_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        self.watchdog.heartbeat()
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

    async def broadcast_command(self, cmd: Dict[str, Any]):
        await self.server.broadcast(cmd)

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
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Core Error: {e}")
                await asyncio.sleep(0.1)

    async def _process_orchestrator_event(self, event: Dict[str, Any]):
        e_type = event.get("type")
        symbol = event.get("symbol")

        if e_type == "MARKET_DATA":
            for b in ["Trend_1", "Indicator_1", "Regime_1"]: self.ipc.xadd(f"stream:{b}", event)
            orders = await self.pos_manager.monitor_and_manage(symbol, event["bid"], event["ask"], event["atr"], mtf_trends=self.ipc.get_state(f"trend_stats:{symbol}"))
            for o in orders:
                if o.get("type") == "PROBABILISTIC_SIGNAL": self.ipc.xadd("stream:orchestrator", o)
                else: await self.server.broadcast(o)

        elif e_type in ["EVIDENCE", "REGIME_STATUS"]:
            self.ipc.xadd("stream:MetaBrain", event)

        elif e_type == "PROBABILISTIC_SIGNAL":
            self.ipc.xadd("stream:Risk_1", event)

        elif e_type == "VALIDATED_TRADE":
            active = await self.ledger.get_active_trades_db(symbol)
            if any(t['action'] == event['action'] for t in active) and not event.get("scaling"):
                return
            self.ipc.xadd("stream:Execution_1", event)

        elif e_type == "EXECUTION_ORDER":
            event["magic"] = self.config.system.global_magic
            event["comment"] = f"AAT{time.strftime('%d%m')}{time.strftime('%H%M%S')}"
            if event.get("t") == "DEC":
                event["id"] = await self.ledger.record_intent(event["s"], event["act"], event["lts"], int(event["sl_p"]), int(event["tp_p"]))
                self.risk_manager.increment_trade_count(event["s"])
                self.ipc.set_state("last_decision", {"ts": time.time(), "msg": f"EXEC {event['act']} {event['s']} @ {event['lts']} lots (Magic: {event['magic']})"})
            await self.server.broadcast(event)

        elif e_type == "CLOSE_ALL":
            await self.server.broadcast({"mgmt": "CLOSE_ALL", "reason": "MANUAL_OR_WATCHDOG"})

    def _update_system_stats(self):
        uptime = time.time() - self.start_time
        stats = {"status": "V4.0-PRO_OPTIMAL" if self.server.clients else "WAITING", "active_clients": len(self.server.clients),
                 "throughput": float(self._msg_counts / uptime) if uptime > 0 else 0, "server_time": time.time()}
        self.ipc.set_state("engine_stats", stats)
        sync_task = asyncio.create_task(self._sync_trades_to_ipc())
        self._background_tasks.add(sync_task)
        sync_task.add_done_callback(self._background_tasks.discard)

    async def _sync_trades_to_ipc(self):
        trades = await self.ledger.get_all_active_trades()
        self.ipc.set_state("active_trades", trades)

    async def _spawn_brain_swarm(self):
        swarm = [(MarketDataBrain, "MarketData_1"), (TrendBrain, "Trend_1"), (IndicatorBrain, "Indicator_1"),
                 (RegimeBrain, "Regime_1"), (RiskBrain, "Risk_1"), (ExecutionBrain, "Execution_1"), (MetaBrain, "MetaBrain"),
                 (MomentumBrain, "Momentum_1"), (StructureBrain, "Structure_1"), (CarryBrain, "Carry_1"), (DayBrain, "Day_1"),
                 (ScalpBrain, "Scalp_1"), (SwingBrain, "Swing_1"), (VsaBrain, "Vsa_1"), (WyckoffBrain, "Wyckoff_1"),
                 (DonchianBrain, "Donchian_1"), (TurtleBrain, "Turtle_1"), (SupertrendBrain, "Supertrend_1")]
        for _, name in swarm: self.ipc.create_stream(f"stream:{name}")
        for i, (brain_cls, name) in enumerate(swarm):
            brain = brain_cls(name=name, ipc=self.ipc)
            self.registry.register(brain)
            self.brains[name] = brain
            brain.start()
            await asyncio.sleep(0.05)

    async def stop(self, *args):
        logger.info("Initiating HiveOrchestrator Shutdown...")
        self.running = False

        # Stop Watchdog
        self.watchdog.stop()

        # Stop Bridge Server
        await self.server.stop()

        # Cancel all background tasks
        if self._background_tasks:
            logger.info(f"Cancelling {len(self._background_tasks)} background tasks...")
            for task in self._background_tasks:
                task.cancel()
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        if self.native_dash: self.native_dash.terminate()
        if self.web_dash: self.web_dash.terminate()
        self.registry.stop_all()
        logger.info("AAT V4.0-PRO Shutdown Complete.")

class MomentumBrain(BaseBrain):
    async def process(self, e): return None
class StructureBrain(BaseBrain):
    async def process(self, e): return None
class CarryBrain(BaseBrain):
    async def process(self, e): return None
class DayBrain(BaseBrain):
    async def process(self, e): return None
class ScalpBrain(BaseBrain):
    async def process(self, e): return None
class SwingBrain(BaseBrain):
    async def process(self, e): return None
class VsaBrain(BaseBrain):
    async def process(self, e): return None
class WyckoffBrain(BaseBrain):
    async def process(self, e): return None
class DonchianBrain(BaseBrain):
    async def process(self, e): return None
class TurtleBrain(BaseBrain):
    async def process(self, e): return None
class SupertrendBrain(BaseBrain):
    async def process(self, e): return None
