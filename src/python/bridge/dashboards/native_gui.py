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
                with dpg.child_window(width=450, height=240, label="System Vitals"):
                    dpg.add_text("SYSTEM VITALS", color=[0, 242, 255])
                    self.equity_tag = dpg.add_text("EQUITY: $0.00")
                    self.dd_tag = dpg.add_text("DRAWDOWN: 0.00%")
                    self.pos_tag = dpg.add_text("ACTIVE POSITIONS: 0")
                    dpg.add_separator()
                    self.decision_tag = dpg.add_text("LAST DECISION: None", color=[255, 200, 100], wrap=400)
                    self.clock_tag = dpg.add_text("SERVER TIME: 00:00:00", color=[100, 100, 100])

                with dpg.child_window(width=450, height=240, label="Engine Orchestrator"):
                    dpg.add_text("V4.0 PARALLEL CORE", color=[0, 242, 255])
                    self.status_tag = dpg.add_text("WAITING", color=[255, 140, 0])
                    self.throughput_tag = dpg.add_text("THROUGHPUT: 0.0 msgs/s")
                    self.latency_tag = dpg.add_text("CORE LATENCY: 0.00ms")
                    self.client_tag = dpg.add_text("MT5 CLIENTS: 0", color=[100, 200, 255])
                    dpg.add_separator()
                    self.inst_tag = dpg.add_text("INSTITUTIONAL LOT: 0.01", color=[200, 200, 200])

            dpg.add_spacer(height=10)
            dpg.add_text("BAYESIAN BRAIN CLUSTER RELIABILITY", color=[0, 242, 255])
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
            dpg.add_text("MARKET INTEL (MTF / BAYESIAN CONFLUENCE)", color=[0, 242, 255])
            dpg.add_separator()
            with dpg.table(tag="IntelTable", header_row=True, borders_innerH=True, borders_outerH=True, resizable=True):
                dpg.add_table_column(label="SYMBOL")
                dpg.add_table_column(label="WIN PROB %")
                dpg.add_table_column(label="TREND (H1)")
                dpg.add_table_column(label="REGIME")
                dpg.add_table_column(label="ATR")

            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=lambda: self.ipc.xadd("stream:orchestrator", {"type": "EMERGENCY_KILL"}), width=150, height=40)
                dpg.add_button(label="FORCE SYNC", callback=lambda: self.ipc.xadd("stream:orchestrator", {"type": "FORCE_SYNC"}), width=150, height=40)

        dpg.create_viewport(title="AAT Phoenix V4.0 PRO - Institutional Proactive HUD", width=1000, height=750)
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

            last_decision = self.ipc.get_state("last_decision", {})
            if last_decision:
                dpg.set_value(self.decision_tag, f"LAST DECISION: {last_decision.get('msg')}")

            inst = self.ipc.get_state("institutional_settings", {})
            dpg.set_value(self.inst_tag, f"INSTITUTIONAL LOT: {inst.get('standard_lot_size', 0.01)}")

            engine = self.ipc.get_state("engine_stats", {})
            if engine:
                status = engine.get('status', 'WAITING')
                dpg.set_value(self.status_tag, status)
                dpg.bind_item_theme(self.status_tag, self.green_theme if "OPTIMAL" in status else self.red_theme)
                dpg.set_value(self.throughput_tag, f"THROUGHPUT: {engine.get('throughput', 0):.1f} msgs/s")
                dpg.set_value(self.latency_tag, f"CORE LATENCY: {engine.get('latency', 0)*1000:.2f}ms")
                dpg.set_value(self.client_tag, f"MT5 CLIENTS: {engine.get('active_clients', 0)}")

            rel_scores = self.ipc.get_state("brain_reliability", {})
            now = time.time()
            for b, row in self.brain_rows.items():
                health = self.ipc.get_state(f"brain_health:{b}", {})
                if health:
                    last_seen = now - health.get("last_heartbeat", 0)
                    if last_seen < 20:
                        dpg.set_value(row["status"], "ONLINE")
                        dpg.bind_item_theme(row["status"], self.green_theme)
                        dpg.set_value(row["lat"], f"{health.get('latency', 0):.2f}ms")
                    else:
                        dpg.set_value(row["status"], "STALE")
                        dpg.bind_item_theme(row["status"], self.red_theme)

                score = rel_scores.get(b, 0.70)
                dpg.set_value(row["rel"], f"{score:.2f}")

            # Market Intel Update
            all_state = self.ipc.get_all_state()
            symbols = list(set([k.split(":")[1] for k in all_state.keys() if k.startswith("intel:")]))

            # Efficient Table Management
            existing_rows = dpg.get_item_children("IntelTable", 1)
            if len(existing_rows) != len(symbols):
                for child in existing_rows: dpg.delete_item(child)
                for s in sorted(symbols):
                    with dpg.table_row(parent="IntelTable", tag=f"Row_{s}"):
                        dpg.add_text(s, tag=f"Cell_Sym_{s}")
                        dpg.add_text("0.5", tag=f"Cell_Prob_{s}")
                        dpg.add_text("NEUTRAL", tag=f"Cell_Trend_{s}")
                        dpg.add_text("NORMAL", tag=f"Cell_Regime_{s}")
                        dpg.add_text("0.0", tag=f"Cell_ATR_{s}")

            for s in sorted(symbols):
                intel = self.ipc.get_state(f"intel:{s}", {})
                trends = self.ipc.get_state(f"trend_stats:{s}", {})
                stats = self.ipc.get_state(f"symbol_stats:{s}", {})

                prob = intel.get("prob", 0.5) * 100
                dpg.set_value(f"Cell_Prob_{s}", f"{prob:.1f}%")
                dpg.bind_item_theme(f"Cell_Prob_{s}", self.green_theme if prob > 70 else (self.red_theme if prob < 30 else {}))
                dpg.set_value(f"Cell_Trend_{s}", trends.get("h1", "NEUTRAL"))
                dpg.set_value(f"Cell_Regime_{s}", intel.get("regime", "NORMAL"))
                dpg.set_value(f"Cell_ATR_{s}", f"{stats.get('atr', 0):.5f}")

        except Exception as e:
            logger.debug(f"HUD refresh skip: {e}")
