import dearpygui.dearpygui as dpg
import time
import logging
from typing import Dict, Any, List
from multiprocessing import Process
from src.python.hive.ipc import HiveIPC

logger = logging.getLogger("AAT_NativeGUI")

class NativeDashboard(Process):
    """V4.0-PRO: Institutional Proactive HUD."""
    def __init__(self, ipc: HiveIPC = None):
        Process.__init__(self)
        self.ipc = ipc
        self.themes = {}

    def run(self):
        dpg.create_context()
        self._setup_themes()

        with dpg.window(label="AAT Phoenix Institutional Pro V4.0", tag="PrimaryWindow"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=450, height=220, label="System Vitals"):
                    dpg.add_text("SYSTEM VITALS", color=[0, 242, 255])
                    self.equity_tag = dpg.add_text("EQUITY: -bash.00")
                    self.dd_tag = dpg.add_text("DRAWDOWN: 0.00%")
                    self.pos_tag = dpg.add_text("ACTIVE POSITIONS: 0")
                    dpg.add_separator()
                    self.decision_tag = dpg.add_text("LAST DECISION: None", color=[255, 200, 100])
                    self.clock_tag = dpg.add_text("SERVER TIME: 00:00:00", color=[100, 100, 100])

                with dpg.child_window(width=450, height=220, label="Engine Orchestrator"):
                    dpg.add_text("V4.0 PARALLEL CORE", color=[0, 242, 255])
                    self.status_tag = dpg.add_text("WAITING", color=[255, 140, 0])
                    self.throughput_tag = dpg.add_text("THROUGHPUT: 0.0 msgs/s")
                    self.latency_tag = dpg.add_text("CORE LATENCY: 0.00ms")
                    self.client_tag = dpg.add_text("MT5 CLIENTS: 0", color=[100, 200, 255])

            dpg.add_spacer(height=10)
            dpg.add_text("BAYESIAN PROBABILITY & RELIABILITY", color=[0, 242, 255])
            dpg.add_separator()
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label="BRAIN UNIT")
                dpg.add_table_column(label="STATUS")
                dpg.add_table_column(label="LATENCY")
                dpg.add_table_column(label="RELIABILITY")
                self.brain_rows = {}
                for b in ["MarketData_1", "Trend_1", "Indicator_1", "Risk_1", "MetaBrain", "Execution_1"]:
                    with dpg.table_row():
                        dpg.add_text(b, color=[56, 189, 248])
                        self.brain_rows[b] = {
                            "status": dpg.add_text("OFFLINE"),
                            "lat": dpg.add_text("0.0"),
                            "rel": dpg.add_text("0.70")
                        }

            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=lambda: self.ipc.xadd("stream:orchestrator", {"type": "EMERGENCY_KILL"}), width=150, height=40)
                dpg.add_button(label="FORCE SYNC", callback=lambda: self.ipc.xadd("stream:orchestrator", {"type": "FORCE_SYNC"}), width=150, height=40)

        dpg.create_viewport(title="AAT Phoenix V4.0 PRO", width=1000, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("PrimaryWindow", True)

        while dpg.is_dearpygui_running():
            self._update_hud()
            dpg.render_dearpygui_frame()
            time.sleep(0.1)
        dpg.destroy_context()

    def _setup_themes(self):
        with dpg.theme() as green:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [57, 255, 20])
        with dpg.theme() as red:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
        self.green_theme = green
        self.red_theme = red

    def _update_hud(self):
        if not self.ipc: return
        try:
            account = self.ipc.get_state("account_stats", {})
            dpg.set_value(self.equity_tag, f"EQUITY: ${account.get('equity', 0):,.2f}")
            dpg.set_value(self.dd_tag, f"DRAWDOWN: {account.get('drawdown', 0):.2f}%")
            dpg.set_value(self.pos_tag, f"ACTIVE POSITIONS: {account.get('pos_count', 0)}")
            dpg.set_value(self.clock_tag, f"SERVER TIME: {time.strftime('%H:%M:%S')}")

            engine = self.ipc.get_state("engine_stats", {})
            if engine:
                dpg.set_value(self.status_tag, engine.get('status', 'WAITING'))
                dpg.set_value(self.throughput_tag, f"THROUGHPUT: {engine.get('throughput', 0):.1f} msgs/s")
                dpg.set_value(self.latency_tag, f"CORE LATENCY: {engine.get('latency', 0)*1000:.2f}ms")
                dpg.set_value(self.client_tag, f"MT5 CLIENTS: {engine.get('active_clients', 0)}")

            for b, row in self.brain_rows.items():
                health = self.ipc.get_state(f"brain_health:{b}", {})
                if health:
                    dpg.set_value(row["status"], "ONLINE")
                    dpg.bind_item_theme(row["status"], self.green_theme)
                    dpg.set_value(row["lat"], f"{health.get('latency', 0):.2f}ms")
        except Exception as e:
            logger.debug(f"HUD refresh skip: {e}")
