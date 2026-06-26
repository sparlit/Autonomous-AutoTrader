# Version: V3.1.0-AUTONOMOUS (Hardened RESTRUCTURE)
import dearpygui.dearpygui as dpg
import multiprocessing as mp
import time
from typing import Dict, Any, List
from shared.memory import SharedState

class KanbanDashboard(mp.Process):
    """10500: High-performance Kanban UI for system telemetry."""
    def __init__(self, shared_state: SharedState):
        super().__init__()
        self.shm = shared_state

    def run(self):
        dpg.create_context()

        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT - KANBAN HUD", width=1200, height=800):
            with dpg.group(horizontal=True):
                # Column 1: Account & Risk
                with dpg.child_window(width=300, height=-1, label="STATION STATUS"):
                    dpg.add_text("CAPITAL TELEMETRY", color=[0, 255, 255])
                    self.equity_tag = dpg.add_text("EQUITY: $0.00")
                    self.drawdown_tag = dpg.add_text("DD: 0.00%")
                    dpg.add_separator()
                    dpg.add_text("RISK PARAMETERS", color=[255, 165, 0])
                    dpg.add_text("MODE: AUTONOMOUS")
                    dpg.add_text("VETO STACK: ACTIVE")

                # Column 2: Market Kanban
                with dpg.child_window(width=400, height=-1, label="MARKET PIPELINE"):
                    dpg.add_text("ACTIVE SYMBOLS", color=[0, 255, 0])
                    self.symbol_list = dpg.add_text("Waiting for data...")
                    dpg.add_separator()
                    self.market_table = dpg.add_table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True)
                    dpg.add_table_column(label="SYMBOL", parent=self.market_table)
                    dpg.add_table_column(label="BID", parent=self.market_table)
                    dpg.add_table_column(label="ASK", parent=self.market_table)

                # Column 3: Brain Confluence
                with dpg.child_window(width=450, height=-1, label="BRAIN CONFLUENCE"):
                    dpg.add_text("CLUSTER HEALTH", color=[255, 0, 255])
                    self.brain_health = dpg.add_text("All Brains Offline")
                    dpg.add_separator()
                    dpg.add_text("LAST DECISIONS", color=[255, 255, 0])
                    self.decision_log = dpg.add_text("No orders dispatched.")

        dpg.create_viewport(title='AAT Kanban Terminal', width=1200, height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            self._update_ui()
            dpg.render_dearpygui_frame()
            time.sleep(0.1)

        dpg.destroy_context()

    def _update_ui(self):
        data = self.shm.get_data()

        # Update Account
        acc = data.get("account", {})
        dpg.set_value(self.equity_tag, f"EQUITY: ${acc.get('equity', 0):,.2f}")
        dpg.set_value(self.drawdown_tag, f"DD: {acc.get('drawdown', 0):.2f}%")

        # Update Market
        symbols = [k.split(":")[1] for k in data.keys() if k.startswith("market:")]
        if symbols:
            dpg.set_value(self.symbol_list, f"WATCHING: {', '.join(symbols)}")
