import dearpygui.dearpygui as dpg
import time
import logging
import os
from typing import Any, Dict
from multiprocessing import Process

logger = logging.getLogger("AAT_NativeDashboard")

class NativeDashboard(Process):
    """10500: Institutional Desktop HUD using Dear PyGui."""
    def __init__(self, ipc: Any = None):
        Process.__init__(self)
        self.ipc = ipc
        self.themes = {}

    def run(self):
        dpg.create_context()
        self._setup_themes()

        with dpg.window(label="AAT PHOENIX ASCENDANT - INSTITUTIONAL HUD", width=980, height=680, tag="PrimaryWindow"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=480, height=220, label="Account Telemetry"):
                    dpg.add_text("REAL-TIME ACCOUNT STATUS", color=[0, 242, 255])
                    self.equity_tag = dpg.add_text("EQUITY: $0.00")
                    self.dd_tag = dpg.add_text("DRAWDOWN: 0.00%")
                    self.pos_tag = dpg.add_text("ACTIVE POSITIONS: 0")
                    dpg.add_separator()
                    self.spread_tag = dpg.add_text("AVG SPREAD: 0.0 pts")
                    self.timer_tag = dpg.add_text("CANDLE TIMER: --:--")
                    self.clock_tag = dpg.add_text("SERVER TIME: 00:00:00", color=[100, 100, 100])

                with dpg.child_window(width=450, height=220, label="Engine Orchestrator"):
                    dpg.add_text("HIVE STATUS", color=[0, 242, 255])
                    self.status_tag = dpg.add_text("WAITING", color=[255, 140, 0])
                    self.msg_rx_tag = dpg.add_text("MSGS RX: 0")
                    self.msg_tx_tag = dpg.add_text("MSGS TX: 0")
                    self.latency_tag = dpg.add_text("LATENCY: 0.00ms")
                    self.reconnect_tag = dpg.add_text("CONNECTIONS: 0", color=[100, 200, 255])

            dpg.add_spacer(height=5)
            dpg.add_text("BRAIN CLUSTER HEALTH & BAYESIAN METRICS", color=[0, 242, 255])
            dpg.add_separator()

            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True, sortable=True):
                dpg.add_table_column(label="BRAIN UNIT")
                dpg.add_table_column(label="PID")
                dpg.add_table_column(label="CPU %")
                dpg.add_table_column(label="MEM (MB)")
                dpg.add_table_column(label="MSGS")
                dpg.add_table_column(label="LATENCY (ms)")
                dpg.add_table_column(label="STATUS")
                dpg.add_table_column(label="LAST SEEN")

                self.brain_rows = {}
                brain_list = [
                    "MarketData_1", "Trend_1", "Indicator_1", "Momentum_1", "Structure_1",
                    "Liquidity_1", "Regime_1", "MetaBrain", "Risk_1", "Execution_1",
                    "Portfolio_1", "Monitoring_1", "Anomaly_1", "SwingMaster", "ScalpMaster",
                    "VSAMaster", "WyckoffMaster", "ICTKillzone"
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
                            "status": dpg.add_text("OFFLINE"),
                            "seen": dpg.add_text("Never")
                        }

            dpg.add_spacer(height=10)
            dpg.add_text("ACTIVE INSTITUTIONAL POSITIONS", color=[0, 242, 255])
            dpg.add_separator()
            with dpg.table(tag="TradesTable", header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True):
                dpg.add_table_column(label="SYMBOL")
                dpg.add_table_column(label="TICKET")
                dpg.add_table_column(label="ACTION")
                dpg.add_table_column(label="LOTS")
                dpg.add_table_column(label="ENTRY")
                dpg.add_table_column(label="SL")
                dpg.add_table_column(label="TP")
                dpg.add_table_column(label="PL ($)")
                dpg.add_table_column(label="PL (PTS)")
                dpg.add_table_column(label="DURATION")
                dpg.add_table_column(label="STATUS")

            self.trade_rows = {} # We will clear and rebuild this table as its dynamic

            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="EMERGENCY KILL", callback=self.kill_switch, width=150, height=40)
                dpg.add_button(label="FORCE SYNC", callback=self.force_sync, width=150, height=40)
                dpg.add_button(label="CLOSE ALL", callback=self.close_all_trades, width=150, height=40)

        dpg.create_viewport(title="AAT Phoenix Proactive Monitor", width=1000, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("PrimaryWindow", True)

        while dpg.is_dearpygui_running():
            self._update_from_ipc()
            dpg.render_dearpygui_frame()
            time.sleep(0.05)

        dpg.destroy_context()

    def _setup_themes(self):
        with dpg.theme() as red:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
        with dpg.theme() as green:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [57, 255, 20])
        with dpg.theme() as orange:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 140, 0])
        with dpg.theme() as gray:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150])
        self.themes = {'red': red, 'green': green, 'orange': orange, 'gray': gray}

    def _update_from_ipc(self):
        if not self.ipc: return
        try:
            dpg.set_value(self.clock_tag, f"SERVER TIME: {time.strftime('%H:%M:%S')}")

            account = self.ipc.get_state("account_stats", {})
            all_state = self.ipc.get_all_state()

            if account:
                dpg.set_value(self.equity_tag, f"EQUITY: ${account.get('equity', 0):,.2f}")
                dd = account.get('drawdown', 0)
                dpg.set_value(self.dd_tag, f"DRAWDOWN: {dd:.2f}%")
                dpg.bind_item_theme(self.dd_tag, self.themes['red'] if dd > 2 else self.themes['green'])
                dpg.set_value(self.pos_tag, f"ACTIVE POSITIONS: {account.get('pos_count', 0)}")
                dpg.set_value(self.spread_tag, f"AVG SPREAD: {account.get('spread', 0):.1f} pts")
                dpg.set_value(self.timer_tag, f"CANDLE TIMER: {account.get('candle_timer', '--:--')}")

            engine = self.ipc.get_state("engine_stats", {})
            if engine:
                dpg.set_value(self.msg_rx_tag, f"MSGS RX: {engine.get('msgs_rx', 0)}")
                dpg.set_value(self.msg_tx_tag, f"MSGS TX: {engine.get('msgs_tx', 0)}")
                dpg.set_value(self.latency_tag, f"LATENCY: {engine.get('latency', 0)*1000:.2f}ms")

                status = engine.get('status', 'WAITING')
                dpg.set_value(self.status_tag, status)
                status_theme = self.themes['green'] if status == 'OPTIMAL' else self.themes['orange']
                dpg.bind_item_theme(self.status_tag, status_theme)

                dpg.set_value(self.reconnect_tag, f"CONNECTIONS: {engine.get('active_clients', 0)}")

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

                        last_hb = health.get("last_heartbeat", 0)
                        last_seen = now - last_hb if last_hb > 0 else 999.9

                        if last_seen < 15:
                            dpg.set_value(row["status"], "ONLINE")
                            dpg.bind_item_theme(row["status"], self.themes['green'])
                            dpg.set_value(row["seen"], f"{last_seen:.1f}s ago")
                        else:
                            dpg.set_value(row["status"], "OFFLINE")
                            dpg.bind_item_theme(row["status"], self.themes['red'])
                            dpg.set_value(row["seen"], "TIMEOUT")

            # Update Running Trades
            active_trades = self.ipc.get_state("active_trades", [])
            # Clear existing rows in TradesTable
            for child in dpg.get_item_children("TradesTable", 1):
                dpg.delete_item(child)

            for t in active_trades:
                with dpg.table_row(parent="TradesTable"):
                    dpg.add_text(t['symbol'], color=[255, 255, 255])
                    dpg.add_text(str(t['ticket']))
                    action_color = [57, 255, 20] if t['action'] == "BUY" else [255, 0, 0]
                    dpg.add_text(t['action'], color=action_color)
                    dpg.add_text(f"{t['lots']:.2f}")
                    dpg.add_text(f"{t['entry_price']:.5f}")
                    dpg.add_text(f"{t['sl_price']:.5f}", color=[255, 100, 100])
                    dpg.add_text(f"{t['tp_price']:.5f}", color=[100, 255, 100])

                    pl_currency = t.get('pl_currency', 0)
                    pl_color = [57, 255, 20] if pl_currency >= 0 else [255, 0, 0]
                    dpg.add_text(f"${pl_currency:,.2f}", color=pl_color)
                    dpg.add_text(f"{t.get('pl_points', 0):.1f}", color=pl_color)

                    dur = t.get('duration', 0)
                    dpg.add_text(f"{int(dur//60)}m {int(dur%60)}s")
                    dpg.add_text(t.get('status', 'OPEN'), color=[0, 242, 255])
        except Exception as e:
            logger.error(f"HUD Update Error: {e}")

    def kill_switch(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"type": "EMERGENCY_KILL"})
    def force_sync(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"type": "FORCE_SYNC"})
    def close_all_trades(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"type": "EXECUTION_ORDER", "t": "CLOSE_ALL"})
