import dearpygui.dearpygui as dpg
import threading
import time
import logging
import os
from typing import Any, Dict, List
from multiprocessing import Process

class NativeDashboard(Process):
    """10501: High-performance Desktop Dashboard pinned to UI core."""
    def __init__(self, ipc: Any = None):
        Process.__init__(self)
        self.ipc = ipc
        self.stats = {"equity": 0.0, "drawdown": 0.0, "status": "INITIALIZING"}
        self.magic = 10501

    def run(self):
        """10502: GUI Main Loop."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - NativeGUI - %(levelname)s - %(message)s")
        logger = logging.getLogger("AAT_NativeGUI")

        logger.info("Initializing Native Dashboard GUI...")

        try:
            dpg.create_context()
        except Exception as e:
            logger.error(f"Failed to create DPG context: {e}")
            return

        # Pre-create Themes for dynamic coloring in DPG 2.x
        with dpg.theme() as self.alert_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 81, 73], category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.active_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [63, 185, 80], category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.neutral_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200], category=dpg.mvThemeCat_Core)

        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT - INSTITUTIONAL MONITOR", width=980, height=680):
            with dpg.group(horizontal=True):
                dpg.add_text("SYSTEM STATUS:", color=[0, 242, 255])
                self.status_tag = dpg.add_text("INITIALIZING", color=[0, 255, 0])
                dpg.add_spacer(width=200)
                dpg.add_text("SERVER CLOCK:")
                self.clock_tag = dpg.add_text("00:00:00")

            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=150, label="Account Telemetry"):
                    dpg.add_text("REAL-TIME CAPITAL", color=[150, 150, 150])
                    self.equity_tag = dpg.add_text("EQUITY: $0.00", color=[255, 255, 255])
                    self.dd_tag = dpg.add_text("DRAWDOWN: 0.00%", color=[0, 255, 0])
                    self.spread_tag = dpg.add_text("AVG SPREAD: 0.0", color=[200, 200, 200])
                    self.timer_tag = dpg.add_text("CANDLE TIMER: --:--", color=[200, 200, 200])

                with dpg.child_window(width=640, height=150, label="Engine Orchestrator"):
                    dpg.add_text("ULTRA-BRIDGE TELEMETRY", color=[150, 150, 150])
                    with dpg.group(horizontal=True):
                        self.msg_rx_tag = dpg.add_text("MSGS RX: 0")
                        dpg.add_spacer(width=50)
                        self.msg_tx_tag = dpg.add_text("MSGS TX: 0")
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
                dpg.add_table_column(label="THROUGHPUT")
                dpg.add_table_column(label="LATENCY (ms)")
                dpg.add_table_column(label="LAST SEEN")

                self.brain_rows = {}
                brain_list = [
                    "MarketData_1", "MarketData_2", "Indicator_1", "Indicator_2", "Indicator_3",
                    "Trend_1", "Trend_2", "Liquidity_1", "Regime_1", "Meta_1",
                    "Contrarian_1", "NewsRisk_1", "Risk_1", "Risk_2", "Execution_1",
                    "Execution_2", "Memory_1", "Portfolio_1", "Monitoring_1", "Anomaly_1"
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
                            "seen": dpg.add_text("0s ago")
                        }

            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=self.kill_switch, width=150, height=40)
                dpg.add_button(label="FORCE RECON", callback=self.force_sync, width=150, height=40)

        dpg.create_viewport(title='AAT Phoenix Proactive Monitor', width=1000, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            self._update_from_ipc()
            dpg.render_dearpygui_frame()

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
            dpg.bind_item_theme(self.dd_tag, self.alert_theme if dd > 2 else self.active_theme)

            spread = account.get('spread', 0)
            dpg.set_value(self.spread_tag, f"AVG SPREAD: {spread:.1f} pts")

            timer = account.get('candle_timer', '--:--')
            dpg.set_value(self.timer_tag, f"CANDLE TIMER: {timer}")

        engine = self.ipc.get_state("engine_stats", {})
        if engine:
            dpg.set_value(self.msg_rx_tag, f"MSGS RX: {engine.get('msgs_rx', 0)}")
            dpg.set_value(self.msg_tx_tag, f"MSGS TX: {engine.get('msgs_tx', 0)}")
            dpg.set_value(self.latency_tag, f"LATENCY: {engine.get('latency', 0)*1000:.2f}ms")
            dpg.set_value(self.status_tag, engine.get('status', 'ACTIVE'))
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
                    dpg.bind_item_theme(row["seen"], self.alert_theme if last_seen > 10 else self.neutral_theme)

    def kill_switch(self):
        logging.critical("USER COMMAND: EMERGENCY KILL SWITCH ACTIVATED.")
        if self.ipc:
            self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "EMERGENCY_KILL"}'})

    def force_sync(self):
        logging.info("USER COMMAND: FORCE SYNC REQUESTED.")
        if self.ipc:
            self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "FORCE_SYNC"}'})
