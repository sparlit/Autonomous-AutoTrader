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
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - NativeGUI - %(levelname)s - %(message)s")
        logger = logging.getLogger("AAT_NativeGUI")

        try:
            dpg.create_context()
        except Exception as e:
            logger.error(f"Failed to create DPG context: {e}")
            return

        with dpg.theme() as self.alert_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 81, 73])

        with dpg.theme() as self.active_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [63, 185, 80])

        with dpg.theme() as self.neutral_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200])

        with dpg.window(label="🦅 AAT PHOENIX ASCENDANT V3.0 - MASTER PRO", width=1200, height=950):
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
                    dpg.add_spacer(height=10)
                    dpg.add_text("THROUGHPUT INTENSITY")
                    self.throughput_bar = dpg.add_progress_bar(default_value=0.0, width=380)

            dpg.add_spacer(height=5)
            dpg.add_text("ACTIVE POSITIONS (SYNCED)", color=[255, 150, 0])
            dpg.add_separator()
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True, height=150, tag="active_trades_table"):
                dpg.add_table_column(label="TICKET")
                dpg.add_table_column(label="SYMBOL")
                dpg.add_table_column(label="ACTION")
                dpg.add_table_column(label="LOTS")
                dpg.add_table_column(label="ENTRY")
                dpg.add_table_column(label="SL")
                dpg.add_table_column(label="TP")
                dpg.add_table_column(label="MANAGED")

            dpg.add_spacer(height=5)
            dpg.add_text("ACTIVE SYMBOL INTELLIGENCE", color=[0, 242, 255])
            dpg.add_separator()

            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True, sortable=True, height=180):
                dpg.add_table_column(label="SYMBOL")
                dpg.add_table_column(label="SPREAD")
                dpg.add_table_column(label="CANDLE")
                dpg.add_table_column(label="TREND")
                dpg.add_table_column(label="SCORE")
                self.symbol_table_id = dpg.last_item()
                self.symbol_rows = {}

            dpg.add_spacer(height=5)
            dpg.add_text("BRAIN CLUSTER MATRIX TELEMETRY (23 CORES)", color=[0, 242, 255])
            dpg.add_separator()

            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True, sortable=True, height=200):
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

        with dpg.window(label="⚙️ System Diagnostics", width=400, height=200, pos=[1010, 0]):
            self.diag_text = dpg.add_text("IPC State: Waiting for data...")

        dpg.create_viewport(title='AAT Phoenix Master Pro Monitor', width=1450, height=950)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            try:
                if time.time() - self.last_ui_update > 0.1:
                    self._update_from_ipc()
                    self.last_ui_update = time.time()
            except Exception as e:
                if "dearpygui" in str(e).lower() and not dpg.is_dearpygui_running(): break
                logger.error(f"UI Update Error: {e}")
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def _update_from_ipc(self):
        if not self.ipc or not dpg.is_dearpygui_running(): return
        all_state = self.ipc.get_all_state()
        if not all_state: return

        dpg.set_value(self.diag_text, f"IPC State: {len(all_state)} keys active.")

        engine = all_state.get("engine_stats", {})
        server_time = engine.get("server_time", time.time())
        dpg.set_value(self.clock_tag, time.strftime("%H:%M:%S", time.localtime(server_time)))

        account = all_state.get("account_stats", {})
        if account:
            equity = account.get('equity', 0)
            dpg.set_value(self.equity_tag, f"EQUITY: ${equity:,.2f}")
            dd = account.get('drawdown', 0)
            dpg.set_value(self.dd_tag, f"DD: {dd:.2f}%")
            dpg.bind_item_theme(self.dd_tag, self.alert_theme if dd > 2 else self.active_theme)
            dpg.set_value(self.pos_tag, f"POS: {account.get('pos_count', 0)}")
            dpg.set_value(self.pnl_progress, 0.5 + (equity % 1000) / 2000)

        sys_params = all_state.get("sys_params", {})
        if sys_params:
            dpg.set_value(self.param_risk, f"RISK/TRADE: {sys_params.get('risk_per_trade_pct', 0):.1f}%")
            dpg.set_value(self.param_dd_limit, f"MAX DD: {sys_params.get('max_drawdown_pct', 0):.1f}%")
            dpg.set_value(self.param_daily_limit, f"DAILY LIMIT: {sys_params.get('daily_loss_limit_pct', 0):.1f}%")
            dpg.set_value(self.param_consensus, f"CONSENSUS: {sys_params.get('consensus_threshold', 0):.1f}%")
            sess_active = sys_params.get('session_active', False)
            dpg.set_value(self.bool_session, f"SESSION: {'ACTIVE' if sess_active else 'INACTIVE'}")
            dpg.bind_item_theme(self.bool_session, self.active_theme if sess_active else self.alert_theme)
            news_safe = sys_params.get('news_safe', True)
            dpg.set_value(self.bool_news, f"NEWS: {'SAFE' if news_safe else 'DANGER'}")
            dpg.bind_item_theme(self.bool_news, self.active_theme if news_safe else self.alert_theme)
            dpg.set_value(self.stat_trades, f"DAILY TRADES: {sys_params.get('daily_trades', 0)}")
            dpg.set_value(self.stat_peak, f"PEAK: ${sys_params.get('peak_equity', 0):,.2f}")

        # 16025: Clear and rebuild active trades table for accuracy
        active_trades = all_state.get("active_trades", [])
        dpg.delete_item("active_trades_table", children_only=True)
        for t in active_trades:
            tk = t["ticket"]
            if tk == 0: continue
            with dpg.table_row(parent="active_trades_table"):
                dpg.add_text(str(tk))
                dpg.add_text(t["symbol"])
                dpg.add_text(t["action"])
                dpg.add_text(f"{t['lots']:.2f}")
                dpg.add_text(f"{t.get('entry_price', 0):.5f}")
                dpg.add_text(f"{t.get('sl_price', 0):.5f}")
                dpg.add_text(f"{t.get('tp_price', 0):.5f}")
                dpg.add_text("YES" if t.get("is_managed") else "NO")

        if engine:
            rx = engine.get('msgs_rx', 0); tx = engine.get('msgs_tx', 0); mps = engine.get('mps', 0.0)
            dpg.set_value(self.msg_rx_tag, f"MSGS RX: {rx}"); dpg.set_value(self.msg_tx_tag, f"MSGS TX: {tx}")
            dpg.set_value(self.mps_tag, f"MPS: {mps:.1f}")
            dpg.set_value(self.latency_tag, f"LATENCY: {engine.get('latency', 0)*1000:.2f}ms")
            dpg.set_value(self.status_tag, engine.get('status', 'ACTIVE'))
            dpg.set_value(self.reconnect_tag, f"CONNECTIONS: {engine.get('active_clients', 0)}")
            dpg.set_value(self.throughput_bar, min(1.0, mps / 100.0))

        for key, sym in all_state.items():
            if key.startswith("symbol_stats:"):
                symbol_name = sym.get("symbol")
                if symbol_name not in self.symbol_rows:
                    with dpg.table_row(parent=self.symbol_table_id):
                        dpg.add_text(symbol_name, color=[255, 255, 255])
                        self.symbol_rows[symbol_name] = {
                            "spread": dpg.add_text("0.0"), "timer": dpg.add_text("--:--"),
                            "trend": dpg.add_text("NEUTRAL"), "score": dpg.add_text("50.0%")
                        }
                row = self.symbol_rows[symbol_name]
                dpg.set_value(row["spread"], f"{sym.get('spread', 0):.1f}")
                dpg.set_value(row["timer"], sym.get('candle_timer', '--:--'))
                dpg.set_value(row["trend"], sym.get('htf', 'NEUTRAL'))
                dpg.set_value(row["score"], f"{sym.get('scr', 0.5)*100:.1f}%")

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
                    is_live = (server_time - health.get("last_heartbeat", 0)) < 5
                    dpg.set_value(row["status"], "LIVE" if is_live else "OFFLINE")
                    dpg.bind_item_theme(row["status"], self.active_theme if is_live else self.alert_theme)

    def kill_switch(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "EMERGENCY_KILL"}'})
    def force_sync(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "FORCE_SYNC"}'})
    def close_all_trades(self):
        if self.ipc: self.ipc.xadd("stream:orchestrator", {"payload": '{"type": "EXECUTION_ORDER", "t": "CLOSE_ALL"}'})
