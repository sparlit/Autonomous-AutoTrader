import dearpygui.dearpygui as dpg
import threading
import time
import logging

class NativeDashboard:
    def __init__(self):
        """Magic: 10501"""
        self.stats = {"equity": 0.0, "drawdown": 0.0, "status": "INITIALIZING"}
        self.magic = 10501

    def _create_gui(self):
        """Magic: 10502"""
        dpg.create_context()
        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT", width=500, height=400):
            dpg.add_text("INSTITUTIONAL PERFORMANCE MONITOR", color=[0, 242, 255])
            dpg.add_separator()
            self.status_tag = dpg.add_text(f"STATUS: {self.stats['status']}")
            self.equity_tag = dpg.add_text(f"EQUITY: ${self.stats['equity']:,.2f}")
            self.dd_tag = dpg.add_text(f"DRAWDOWN: {self.stats['drawdown']:.2f}%")

            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=self.kill_switch, width=150, height=40)
                dpg.add_button(label="RESET PEAK", callback=self.reset_peak, width=150, height=40)

        dpg.create_viewport(title='AAT Phoenix Proactive Monitor', width=520, height=440)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            # Update values from internal state
            dpg.set_value(self.status_tag, f"STATUS: {self.stats['status']}")
            dpg.set_value(self.equity_tag, f"EQUITY: ${self.stats['equity']:,.2f}")
            dpg.set_value(self.dd_tag, f"DRAWDOWN: {self.stats['drawdown']:.2f}%")
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def start_async(self):
        """Magic: 10503"""
        self.thread = threading.Thread(target=self._create_gui, daemon=True)
        self.thread.start()
        logging.info("Native GUI started in background thread.")

    def update_stats(self, equity: float, drawdown: float, status: str = "ACTIVE"):
        """Magic: 10504"""
        self.stats["equity"] = equity
        self.stats["drawdown"] = drawdown
        self.stats["status"] = status

    def kill_switch(self):
        """Magic: 10505"""
        logging.critical("USER COMMAND: EMERGENCY KILL SWITCH ACTIVATED.")
        # Logic to send KILL to all agents would go here

    def reset_peak(self):
        """Magic: 10506"""
        logging.info("USER COMMAND: PEAK EQUITY RESET.")
