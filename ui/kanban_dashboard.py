# Version: V3.1.3-AUTONOMOUS (Hardened RESTRUCTURE)
import dearpygui.dearpygui as dpg
import multiprocessing as mp
import time
from typing import Dict, Any
from shared.memory import SharedState

class KanbanDashboard(mp.Process):
    """10500: High-performance Kanban UI for system telemetry and manual override."""
    def __init__(self, shared_state: SharedState, control_state: SharedState):
        super().__init__()
        self.shm = shared_state
        self.control = control_state

    def run(self):
        dpg.create_context()

        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT - KANBAN HUD", width=1250, height=850):
            with dpg.group(horizontal=True):
                # Column 1: Station Status & Command (Manual Controls)
                with dpg.child_window(width=300, height=-1, label="STATION STATUS"):
                    dpg.add_text("CAPITAL TELEMETRY", color=[0, 255, 255])
                    self.equity_tag = dpg.add_text("EQUITY: $0.00")
                    self.drawdown_tag = dpg.add_text("DD: 0.00%")
                    dpg.add_separator()

                    dpg.add_text("COMMAND CENTER", color=[255, 0, 0])
                    self.pause_btn = dpg.add_button(label="SYSTEM PAUSE", callback=self.toggle_pause, width=280, height=40)
                    self.manual_btn = dpg.add_button(label="MANUAL MODE: OFF", callback=self.toggle_manual, width=280, height=40)
                    dpg.add_separator()

                    dpg.add_text("PARAMETER TUNING", color=[255, 165, 0])
                    dpg.add_slider_float(label="Risk/Trade %", default_value=1.0, min_value=0.1, max_value=5.0, callback=self.update_risk)
                    dpg.add_slider_float(label="Consensus", default_value=0.7, min_value=0.5, max_value=0.9, callback=self.update_consensus)

                # Column 2: Market Pipeline (Symbol Kanban)
                with dpg.child_window(width=450, height=-1, label="MARKET PIPELINE"):
                    dpg.add_text("ACTIVE PIPELINE", color=[0, 255, 0])
                    self.market_table = dpg.add_table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True)
                    dpg.add_table_column(label="SYMBOL", parent=self.market_table)
                    dpg.add_table_column(label="BID/ASK", parent=self.market_table)
                    dpg.add_table_column(label="SPREAD", parent=self.market_table)
                    dpg.add_table_column(label="STATUS", parent=self.market_table)
                    self.market_rows = {}

                # Column 3: Brain Confluence & Signals
                with dpg.child_window(width=450, height=-1, label="BRAIN CONFLUENCE"):
                    dpg.add_text("HIVE CLUSTER HEALTH", color=[255, 0, 255])
                    self.health_table = dpg.add_table(header_row=True, borders_innerH=True, borders_outerH=True)
                    dpg.add_table_column(label="BRAIN", parent=self.health_table)
                    dpg.add_table_column(label="LATENCY", parent=self.health_table)
                    dpg.add_table_column(label="PULSE", parent=self.health_table)
                    self.health_rows = {}

                    dpg.add_separator()
                    dpg.add_text("LIVE SIGNAL STREAM", color=[255, 255, 0])
                    self.signal_log = dpg.add_listbox(items=[], width=430, num_items=20)

        dpg.create_viewport(title='AAT Phoenix Kanban Terminal', width=1250, height=850)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            self._update_ui()
            dpg.render_dearpygui_frame()
            time.sleep(0.05) # 50ms UI Refresh

        dpg.destroy_context()

    def toggle_pause(self):
        c = self.control.get_data()
        new_state = not c.get("paused", False)
        self.control.update_key("paused", new_state)
        dpg.set_item_label(self.pause_btn, "RESUME SYSTEM" if new_state else "SYSTEM PAUSE")

    def toggle_manual(self):
        c = self.control.get_data()
        new_state = not c.get("manual_mode", False)
        self.control.update_key("manual_mode", new_state)
        dpg.set_item_label(self.manual_btn, f"MANUAL MODE: {'ON' if new_state else 'OFF'}")

    def update_risk(self, sender, val):
        self.control.update_key("param_risk", val)

    def update_consensus(self, sender, val):
        self.control.update_key("param_consensus", val)

    def _update_ui(self):
        data = self.shm.get_data()

        # Account
        acc = data.get("account", {})
        dpg.set_value(self.equity_tag, f"EQUITY: ${acc.get('equity', 0):,.2f}")
        dd = acc.get('drawdown', 0)
        dpg.set_value(self.drawdown_tag, f"DRAWDOWN: {dd:.2f}%")

        # Market Table Sync
        symbols = [k.split(":")[1] for k in data.keys() if k.startswith("market:")]
        for s in symbols:
            m = data.get(f"market:{s}", {})
            bid, ask = m.get("bid", 0), m.get("ask", 0)
            spread = (ask - bid) * 100000 if "JPY" not in s else (ask - bid) * 1000
            if s not in self.market_rows:
                with dpg.table_row(parent=self.market_table):
                    self.market_rows[s] = {
                        "sym": dpg.add_text(s),
                        "price": dpg.add_text(f"{bid:.5f}/{ask:.5f}"),
                        "spread": dpg.add_text(f"{spread:.1f}"),
                        "status": dpg.add_text("ACTIVE", color=[0, 255, 0])
                    }
            else:
                dpg.set_value(self.market_rows[s]["price"], f"{bid:.5f}/{ask:.5f}")
                dpg.set_value(self.market_rows[s]["spread"], f"{spread:.1f}")
