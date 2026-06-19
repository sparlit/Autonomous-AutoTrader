import datetime
<<<<<<< HEAD
import json
import os
from typing import Dict, Any, List
=======
from typing import Dict, Any
>>>>>>> origin/main

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_trades = 0
        self.last_trade_time = None
<<<<<<< HEAD
        self.news_events: List[Dict[str, Any]] = []
        self.peak_equity = 0.0
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.news_events = json.load(f)

    def is_session_active(self) -> bool:
=======

    def is_session_active(self) -> bool:
        """Check if London or New York session is active."""
        # For testing purposes, we can allow a bypass or just return True if mocked
        # In production, this uses UTC time
>>>>>>> origin/main
        now = datetime.datetime.now(datetime.UTC).time()
        london_start = datetime.time(8, 0)
        london_end = datetime.time(16, 0)
        ny_start = datetime.time(13, 0)
        ny_end = datetime.time(21, 0)
<<<<<<< HEAD
        return (london_start <= now <= london_end) or (ny_start <= now <= ny_end)

    def is_news_safe(self) -> bool:
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                event_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                diff = abs((event_time - now).total_seconds()) / 60.0
                if diff <= 30.0: return False
            except Exception: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """Calculate lots and point-based SL/TP offsets."""
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}

        risk_currency = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_dist = atr * 2

        # Calculate number of ticks for SL
        num_ticks = sl_dist / tick_size if tick_size > 0 else 0
        lots = risk_currency / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size

        # Convert distances to points (integers for MT5)
        # Assumes points = tick_size
        sl_pts = int(sl_dist / tick_size)
        tp_pts = int((sl_dist * 2) / tick_size) # 2R

        return {
            "lots": max(self.config.risk.min_lot_size, round(lots, 2)),
            "sl_pts": sl_pts,
            "tp_pts": tp_pts
        }

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        if not ignore_session and not self.is_session_active():
            return {"safe": False, "reason": "Outside trading sessions"}
        if not self.is_news_safe():
            return {"safe": False, "reason": "High impact news pending"}
        if self.daily_trades >= 5:
            return {"safe": False, "reason": "Daily trade limit reached"}

        # Relative Drawdown Check
        if self.peak_equity > 0:
            current_dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if current_dd > self.config.risk.max_drawdown_pct:
                return {"safe": False, "reason": f"Max Relative Drawdown reached ({current_dd:.2f}%)"}

        params = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)

        return {
            "safe": True,
            "lots": params["lots"],
            "sl_pts": params["sl_pts"],
            "tp_pts": params["tp_pts"],
=======

        return (london_start <= now <= london_end) or (ny_start <= now <= ny_end)

    def is_news_safe(self) -> bool:
        return True

    def validate_trade(self, symbol: str, action: str, current_equity: float, ignore_session: bool = False) -> Dict[str, Any]:
        if not ignore_session and not self.is_session_active():
            return {"safe": False, "reason": "Outside trading sessions"}

        if not self.is_news_safe():
            return {"safe": False, "reason": "High impact news pending"}

        if self.daily_trades >= 5:
            return {"safe": False, "reason": "Daily trade limit reached"}

        risk_amount = current_equity * (self.config.risk.risk_per_trade_pct / 100)
        lots = 0.1

        return {
            "safe": True,
            "lots": lots,
>>>>>>> origin/main
            "action": action,
            "symbol": symbol
        }
