import dearpygui.dearpygui as dpg
import time
import logging
import os
from typing import Any, Dict, List
from multiprocessing import Process

class NativeDashboard(Process):
    """10501: High-performance Desktop Dashboard pinned to UI core - Master Pro Edition."""
    def __init__(self, ipc: Any = None):
        Process.__init__(self)
        self.ipc = ipc
        self.stats = {"equity": 0.0, "drawdown": 0.0, "status": "INITIALIZING"}
        self.magic = 10501
        self.last_ui_update = 0

    def run(self):
        """10502: GUI Main Loop."""
        logger = logging.getLogger("AAT_NativeGUI")

        # 10502: Windows-compatible GUI initialization

        try:
            dpg.create_context()
        except Exception as e:
            logger.error(f"Failed to create DPG context: {e}")
            return

        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT - INSTITUTIONAL MONITOR", width=980, height=680):
            with dpg.group(horizontal=True):
                dpg.add_text("SYSTEM STATUS:")
                self.status_tag = dpg.add_text("OPTIMAL", color=[0, 255, 0])
                dpg.add_spacer(width=200)
                dpg.add_text("SERVER CLOCK:")
                self.clock_tag = dpg.add_text("00:00:00")

            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=350, height=220, label="Account Telemetry"):
                    dpg.add_text("REAL-TIME CAPITAL", color=[150, 150, 150])
                    self.equity_tag = dpg.add_text("EQUITY: -bash.00", color=[255, 255, 255])
                    with dpg.group(horizontal=True):
                        self.dd_tag = dpg.add_text("DD: 0.00%", color=[0, 255, 0])
                        dpg.add_spacer(width=20)
                        self.pos_tag = dpg.add_text("POS: 0", color=[0, 242, 255])
                    self.spread_tag = dpg.add_text("AVG SPREAD: 0.0", color=[200, 200, 200])
                    self.timer_tag = dpg.add_text("CANDLE TIMER: --:--", color=[200, 200, 200])
                    dpg.add_spacer(height=5)
                    dpg.add_text("P&L PROGRESS")
                    self.pnl_progress = dpg.add_progress_bar(default_value=0.5, width=320)

                with dpg.child_window(width=400, height=220, label="System Control Parameters"):
                    dpg.add_text("LIVE CONSTANTS & LIMITS", color=[0, 242, 255])
                    with dpg.group(horizontal=True):
                        self.param_risk = dpg.add_text("RISK/TRADE: 0.0%")
                        dpg.add_spacer(width=20)
                        self.param_dd_limit = dpg.add_text("MAX DD: 0.0%")
                    with dpg.group(horizontal=True):
                        self.param_daily_limit = dpg.add_text("DAILY LIMIT: 0.0%")
                        dpg.add_spacer(width=20)
                        self.param_consensus = dpg.add_text("CONSENSUS: 0.0%")

                    dpg.add_separator()
                    dpg.add_text("OPERATIONAL BOOLEANS")
                    with dpg.group(horizontal=True):
                        self.bool_session = dpg.add_text("SESSION: ACTIVE")
                        dpg.add_spacer(width=20)
                        self.bool_news = dpg.add_text("NEWS: SAFE")
                    with dpg.group(horizontal=True):
                        self.stat_trades = dpg.add_text("DAILY TRADES: 0")
                        dpg.add_spacer(width=20)
                        self.stat_peak = dpg.add_text("PEAK: $0.00")

                with dpg.child_window(width=400, height=220, label="Engine Orchestrator"):
                    dpg.add_text("ULTRA-BRIDGE TELEMETRY", color=[150, 150, 150])
                    with dpg.group(horizontal=True):
                        self.msg_rx_tag = dpg.add_text("MSGS RX: 0")
                        dpg.add_spacer(width=50)
                        self.msg_tx_tag = dpg.add_text("MSGS TX: 0")
                    self.mps_tag = dpg.add_text("MPS: 0.0")
                    self.latency_tag = dpg.add_text("LATENCY: 0.00ms")
                    self.reconnect_tag = dpg.add_text("CONNECTIONS: 0", color=[100, 200, 255])

            dpg.add_spacer(height=5)
            dpg.add_text("BRAIN CLUSTER HEALTH & BAYESIAN METRICS", color=[0, 242, 255])
            dpg.add_separator()

            # Enhanced Table for Brains
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True, sortable=True):
                dpg.add_table_column(label="BRAIN UNIT")
                dpg.add_table_column(label="PID")
                dpg.add_table_column(label="CPU %")
                dpg.add_table_column(label="MEM (MB)")
                dpg.add_table_column(label="MSGS")
                dpg.add_table_column(label="LATENCY (ms)")
                dpg.add_table_column(label="STATUS")

                self.brain_rows = {}
                brain_list = [
                    "MarketData_1", "MarketData_2", "Indicator_1", "Indicator_2", "Indicator_3",
                    "Trend_1", "Trend_2", "Liquidity_1", "Momentum_1", "Structure_1",
                    "Regime_1", "Meta_1", "Contrarian_1", "NewsRisk_1", "Correlation_1",
                    "Risk_1", "Risk_2", "Execution_1", "Execution_2", "Memory_1",
                    "Portfolio_1", "Monitoring_1", "Anomaly_1"
                ]
                for brain in brain_list:
                    with dpg.table_row():
                        dpg.add_text(brain, color=[56, 189, 248])
                        self.brain_rows[brain] = {
                            "pid": dpg.add_text("0"),
                            "cpu": dpg.add_text("0.0"),
                            "mem": dpg.add_text("0.0"),
                            "count": dpg.add_text("0"),
                            "lat": dpg.add_text("0.0"),
                            "status": dpg.add_text("OFFLINE")
                        }

            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=self.kill_switch, width=150, height=40)
                dpg.add_button(label="FORCE SYNC", callback=self.force_sync, width=150, height=40)
                dpg.add_button(label="CLOSE ALL", callback=self.close_all_trades, width=150, height=40)

        dpg.create_viewport(title='AAT Phoenix Proactive Monitor', width=1000, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            self._update_from_ipc()
            dpg.render_dearpygui_frame()
            time.sleep(0.01)

        dpg.destroy_context()

    def _update_from_ipc(self):
        if not self.ipc: return

        # Update Clock
        dpg.set_value(self.clock_tag, time.strftime("%H:%M:%S"))

        # Update Global Stats
        account = self.ipc.get_state("account_stats", {})
        if account:
            dpg.set_value(self.equity_tag, f"EQUITY: ${account.get('equity', 0):,.2f}")
            dd = account.get('drawdown', 0)
            dpg.set_value(self.dd_tag, f"DRAWDOWN: {dd:.2f}%")
            dpg.set_item_color(self.dd_tag, dpg.mvPlotCol_Text, [255, 0, 0] if dd > 2 else [0, 255, 0])

            spread = account.get('spread', 0)
            dpg.set_value(self.spread_tag, f"AVG SPREAD: {spread:.1f} pts")

            timer = account.get('candle_timer', '--:--')
            dpg.set_value(self.timer_tag, f"CANDLE TIMER: {timer}")

        engine = self.ipc.get_state("engine_stats", {})
        if engine:
            rx = engine.get('msgs_rx', 0); tx = engine.get('msgs_tx', 0); mps = engine.get('mps', 0.0)
            dpg.set_value(self.msg_rx_tag, f"MSGS RX: {rx}"); dpg.set_value(self.msg_tx_tag, f"MSGS TX: {tx}")
            dpg.set_value(self.mps_tag, f"MPS: {mps:.1f}")
            dpg.set_value(self.latency_tag, f"LATENCY: {engine.get('latency', 0)*1000:.2f}ms")
            dpg.set_value(self.status_tag, engine.get('status', 'ACTIVE'))
            status = engine.get('status', 'ACTIVE')
            status_color = [0, 255, 0] if status == 'OPTIMAL' else ([255, 165, 0] if status == 'WAITING' else [255, 0, 0])
            dpg.set_item_color(self.status_tag, dpg.mvPlotCol_Text, status_color)
            dpg.set_value(self.reconnect_tag, f"CONNECTIONS: {engine.get('active_clients', 0)}")

        # Update Brain Table
        all_state = self.ipc.get_all_state()
        now = time.time()
        for key, health in all_state.items():
            if key.startswith("brain_health:"):
                name = health.get("name")
                if name in self.brain_rows:
                    row = self.brain_rows[name]
                    dpg.set_value(row["pid"], str(health.get("pid")))
                    dpg.set_value(row["cpu"], f"{health.get('cpu', 0):.1f}%")
                    dpg.set_value(row["mem"], f"{health.get('mem', 0):.1f}")
                    dpg.set_value(row["count"], str(health.get("count", 0)))
                    dpg.set_value(row["lat"], f"{health.get('latency', 0):.2f}")
                    last_seen = now - health.get("last_seen", now)
                    dpg.set_value(row["seen"], f"{last_seen:.1f}s ago")
                    dpg.set_item_color(row["seen"], dpg.mvPlotCol_Text, [255, 0, 0] if last_seen > 10 else [200, 200, 200])

    def kill_switch(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "EMERGENCY_KILL"}'})
    def force_sync(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "FORCE_SYNC"}'})
    def close_all_trades(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "EXECUTION_ORDER", "t": "CLOSE_ALL"}'})
