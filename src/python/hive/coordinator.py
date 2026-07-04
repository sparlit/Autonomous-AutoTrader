import asyncio
import logging
import time
import ujson as json
import pandas as pd
from typing import Dict, Any, List, Optional
from src.python.hive.ipc import get_ipc
from src.python.bridge.server import BridgeServer
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager
from src.python.execution.manager import PositionManager
from src.python.analyst.price_action import SMCAnalyst
from src.python.brains.registry import BrainRegistry
from src.python.brains.specialized import *
from src.python.brains.consensus import MetaBrain
from src.python.hive.config import load_config
from src.python.hive.hardware_analyst import HardwareAnalyst

logger = logging.getLogger("AAT_Orchestrator")

class HiveOrchestrator:
    """
    10000: The Institutional Core (V3.3.0-ASCENDANT).
    Central event loop for cross-process brain coordination and bridge management.
    """
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        self.config = load_config()
        self.credentials = credentials
        self.ipc = get_ipc()
        self.server = BridgeServer(
            host=self.config.bridge.host,
            port=self.config.bridge.port,
            on_message_cb=self._bridge_callback_wrapper
        )
        self.ledger = TradeLedger()
        self.risk_manager = RiskManager(self.ipc)
        self.smc = SMCAnalyst()
        self.pos_manager = PositionManager(self.ledger, self.risk_manager)
        self.registry = BrainRegistry()
        self.hardware = HardwareAnalyst()
        self.running = True
        self.start_time = time.time()
        self._msg_counts = 0

    async def _bridge_callback_wrapper(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper to match BridgeServer callback signature."""
        return await self._handle_bridge_message(message)

    async def run(self):
        """10010: Orchestrator entry point."""
        logger.info("Initializing V3.3.0-ASCENDANT Core...")

        # 1. Database and Shared Memory
        await self.ledger.init_db()
        self.ipc.clear_memory()

        # Pre-initialize MUST-HAVE streams
        self.ipc.create_stream("stream:orchestrator")
        self.ipc.create_stream("stream:learning_events")

        # 2. Start Brains
        await self._spawn_brain_swarm()

        # 3. Start Bridge Server
        asyncio.create_task(self.server.start())

        # 4. Start Event Loop
        logger.info("AAT Orchestrator fully operational.")
        await self._orchestration_loop()

    async def _handle_bridge_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """10011: Protocol bridge handler for MT5 packets."""
        m_type = message.get("t")

        if m_type == "HB": # Heartbeat
            self.ipc.set_state("account_stats", {
                "equity": float(message.get("eq", 0.0)),
                "drawdown": float(message.get("dd", 0.0)),
                "pos_count": int(message.get("pc", 0)),
                "spread": float(message.get("sp", 0.0)),
                "candle_timer": message.get("ct", "--:--"),
                "last_hb": time.time()
            })
            self.ipc.xadd("stream:Portfolio_1", {"type": "HB", **message})
            return {"t": "ACK"}

        elif m_type == "DP": # Data Push
            message["type"] = "MARKET_DATA_RAW"
            self.ipc.xadd("stream:MarketData_1", message)
            return {"t": "ACK"}

        elif m_type == "T_ACK":
            internal_id = message.get("id")
            ticket = message.get("tk")
            if ticket and ticket > 0:
                await self.ledger.confirm_trade(internal_id, ticket, 0, 0, 0)
            return {"t": "ACK"}

        elif m_type == "SYNC":
            tickets = message.get("tk", [])
            for t in tickets:
                await self.ledger.update_trade_from_sync(
                    t['tk'], t['s'], t['act'], t['vol'], float(t.get('en', 0)), float(t.get('sl', 0)), float(t.get('tp', 0))
                )
            active_tickets = [t["tk"] for t in tickets]
            await self.ledger.prune_trades(active_tickets)
            return {"t": "SYNC_ACK"}

        return {"t": "SYNC_REQ"}

    async def _orchestration_loop(self):
        """10012: The central event bus reader."""
        logger.info("Event Bus listener active.")
        while self.running:
            try:
                # Telemetry: Check Queue Depth
                q = self.ipc.get_queue("stream:orchestrator")
                q_depth = q.qsize() if hasattr(q, "qsize") else 0

                messages = self.ipc.xread({"stream:orchestrator": "0"}, count=50)
                if messages:
                    for stream, msgs in messages:
                        for msg_id, data in msgs:
                            self._msg_counts += 1
                            event = json.loads(data[b'payload'])
                            await self._process_orchestrator_event(event)
                    await asyncio.sleep(0.005)
                else:
                    await asyncio.sleep(0.02)

                self._update_system_stats(q_depth)
            except Exception as e:
                logger.error(f"Orchestration Loop Error: {e}")
                await asyncio.sleep(0.1)

    async def _process_orchestrator_event(self, event: Dict[str, Any]):
        """10013: Institutional Event Routing."""
        e_type = event.get("type")

        if e_type == "MARKET_DATA":
            symbol = event.get("symbol")
            # 10020: Robust value extraction with defaults to prevent None arithmetic errors
            bid = float(event.get("bid") or 0.0)
            ask = float(event.get("ask") or 0.0)
            atr = float(event.get("atr") or 0.0)

            if bid == 0.0 or ask == 0.0: return

            ltf_df = pd.DataFrame(event.get("ltf", []))
            smc_data = None
            if not ltf_df.empty:
                if isinstance(event["ltf"][0], list): ltf_df.columns = ["o", "h", "l", "c", "t", "v"]
                smc_data = self.smc.detect_market_structure(ltf_df, atr)

            mtf_trends = self.ipc.get_state(f"trend_stats:{symbol}", {})
            orders = await self.pos_manager.monitor_and_manage(symbol, bid, ask, atr, smc_data=smc_data, mtf_trends=mtf_trends)
            for order in orders:
                if order.get("type") == "PROBABILISTIC_SIGNAL":
                    self.ipc.xadd("stream:orchestrator", order)
                else:
                    order["magic"] = self.config.system.global_magic
                    await self.server.broadcast(order)

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
            self.ipc.set_state("last_decision", {"msg": f"VETO: {event.get('reason')} for {event.get('symbol')}", "time": time.time()})
            self.ipc.xadd("stream:MetaBrain", event)
            self.ipc.xadd("stream:Risk_1", event)

        elif e_type == "VALIDATED_TRADE":
            self.ipc.xadd("stream:Execution_1", event)

        elif e_type == "EXECUTION_ORDER":
            event["magic"] = self.config.system.global_magic
            if event.get("t") == "DEC":
                internal_id = await self.ledger.record_intent(
                    event["s"], event["act"], float(event["lts"]), float(event.get("sl_p", 100)), float(event.get("tp_p", 100))
                )
                event["id"] = internal_id
                self.risk_manager.increment_trade_count(event["s"])

            self.ipc.set_state("last_decision", {"msg": f"{event.get('act')} {event.get('s')} at {event.get('lts')} lots", "time": time.time()})
            await self.server.broadcast(event)

        elif e_type == "TELEMETRY":
            hw = self.ipc.get_state("hardware_report", {})
            telemetry_msg = {
                "t": "TLM", "s": event["symbol"], "st": "OPTIMAL" if self.server.clients else "WAITING",
                "scr": float(event.get("scr", 0.0)), "htf": event.get("htf", "NEUTRAL"),
                "dd": float(self.ipc.get_state("account_stats", {}).get("drawdown", 0.0)),
                "pc": int(self.ipc.get_state("account_stats", {}).get("pos_count", 0)),
                "tier": hw.get("tier", "UNKNOWN")
            }
            await self.server.broadcast(telemetry_msg)

    def _update_system_stats(self, q_depth: int):
        stats = {
            "status": "OPTIMAL" if self.server.clients else "WAITING",
            "active_clients": len(self.server.clients),
            "msgs_rx": self.server.stats["msgs_rx"],
            "msgs_tx": self.server.stats["msgs_tx"],
            "latency": float(self.server.stats["last_latency"]),
            "q_depth": int(q_depth),
            "throughput": float(self._msg_counts / (time.time() - self.start_time)) if time.time() > self.start_time else 0.0,
            "server_time": time.time()
        }
        self.ipc.set_state("engine_stats", stats)
        asyncio.create_task(self._sync_trades_to_ipc())
        asyncio.create_task(self._process_learning_events())

    async def _process_learning_events(self):
        try:
            msgs = self.ipc.xread({"stream:learning_events": "0"}, count=10)
            if msgs:
                for stream, stream_msgs in msgs:
                    for _, data in stream_msgs:
                        event = json.loads(data[b'payload'])
                        history = self.ipc.get_state("learning_history", [])
                        history.append({**event, "ts": time.time()})
                        self.ipc.set_state("learning_history", history[-50:])
        except: logger.debug("Learning history sync skipped")

    async def _sync_trades_to_ipc(self):
        trades = await self.ledger.get_all_active_trades()
        now = time.time()
        enriched_trades = []
        for t in trades:
            symbol = t['symbol']
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            bid = float(s_stats.get("bid") or 0.0)
            ask = float(s_stats.get("ask") or 0.0)
            tick_val = float(s_stats.get("tick_val") or 10.0)
            tick_size = float(s_stats.get("tick_size") or 0.0001)

            if bid > 0 and ask > 0:
                current_price = bid if t['action'] == "BUY" else ask
                diff = (current_price - float(t['entry_price'])) if t['action'] == "BUY" else (float(t['entry_price']) - current_price)
                t['pl_points'] = float(diff / tick_size) if tick_size > 0 else 0.0
                t['pl_currency'] = float(t['lots'] * t['pl_points'] * tick_val) if tick_size > 0 else 0.0
            else:
                t['pl_points'] = 0.0
                t['pl_currency'] = 0.0

            t['duration'] = float(now - t['timestamp'])
            enriched_trades.append(t)

        self.ipc.set_state("active_trades", enriched_trades)

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

        self.ipc.create_stream("stream:orchestrator")
        for _, name in swarm_classes:
            self.ipc.create_stream(f"stream:{name}")

        affinity_map = self.hardware.get_optimized_affinity_map(len(swarm_classes))

        for i, (brain_cls, name) in enumerate(swarm_classes):
            brain = brain_cls(name=name, ipc=self.ipc)
            brain.cpu_affinity = affinity_map.get(i)
            self.registry.register(brain)
            brain.start()
            await asyncio.sleep(0.1)

    def stop(self, *args):
        self.running = False
        self.registry.stop_all()
        logger.info("AAT V3.3.0 Shutdown Complete.")
