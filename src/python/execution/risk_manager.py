import datetime
import json
import os
import logging
import sys
from typing import Dict, Any, List

# Import Rust Core for position sizing precision
sys.path.append(os.path.join(os.path.dirname(__file__), '../bridge'))
try:
    import aat_institutional_core as aat_rust_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

logger = logging.getLogger("AAT_RiskManager")

class RiskManager:
    def __init__(self, config):
        """Magic: 60001"""
        self.config = config
        self.daily_trades = 0
        self.news_events: List[Dict[str, Any]] = []
        self.peak_equity = 0.0
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        """Magic: 60002"""
        if os.path.exists(path):
            try:
                with open(path, "r") as f: self.news_events = json.load(f)
                logger.info(f"Risk: Loaded {len(self.news_events)} news events.")
            except Exception as e:
                logger.error(f"News Load Error: {e}")

    def is_session_active(self) -> bool:
        """Magic: 60003"""
        now = datetime.datetime.now(datetime.UTC).time()
        l_start = datetime.time(8, 0); l_end = datetime.time(16, 0)
        n_start = datetime.time(13, 0); n_end = datetime.time(21, 0)
        return (l_start <= now <= l_end) or (n_start <= now <= n_end)

    def is_news_safe(self) -> bool:
        """Magic: 60004"""
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                e_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                if e_time.tzinfo is None: e_time = e_time.replace(tzinfo=datetime.UTC)
                diff_mins = abs((e_time - now).total_seconds()) / 60.0
                if diff_mins <= 30.0 and event.get("impact") == "HIGH":
                    return False
            except: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """Magic: 60005"""
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}

        sl_dist = atr * 2.0

        # Tier 3: Rust-Precision Position Sizing
        if RUST_AVAILABLE:
            lots = aat_rust_core.calculate_position_size_v3(equity, self.config.risk.risk_per_trade_pct, sl_dist, tick_val, tick_size)
        else:
            risk_amount = equity * (self.config.risk.risk_per_trade_pct / 100.0)
            num_ticks = sl_dist / tick_size if tick_size > 0 else 0
            lots = risk_amount / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size

        return {
            "lots": max(self.config.risk.min_lot_size, round(lots, 2)),
            "sl_pts": int(sl_dist / tick_size),
            "tp_pts": int((sl_dist * 1.5) / tick_size)
        }

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """Magic: 60006"""
        if not ignore_session and not self.is_session_active(): return {"safe": False, "reason": "SESS"}
        if not self.is_news_safe(): return {"safe": False, "reason": "NEWS"}
        if self.daily_trades >= 5: return {"safe": False, "reason": "LIMIT"}

        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct: return {"safe": False, "reason": "DD"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
