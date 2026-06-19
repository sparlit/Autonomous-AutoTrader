import datetime
import json
import os
from typing import Dict, Any, List

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_trades = 0
        self.last_trade_time = None
        self.news_events: List[Dict[str, Any]] = []
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.news_events = json.load(f)

    def is_session_active(self) -> bool:
        now = datetime.datetime.now(datetime.UTC).time()
        london_start = datetime.time(8, 0)
        london_end = datetime.time(16, 0)
        ny_start = datetime.time(13, 0)
        ny_end = datetime.time(21, 0)
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

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, current_price: float) -> Dict[str, Any]:
        if atr <= 0:
            return {"lots": self.config.risk.min_lot_size, "sl": 0, "tp": 0}

        risk_currency = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_dist = atr * 2

        if action == "BUY":
            sl = current_price - sl_dist
            tp = current_price + (sl_dist * 2)
        else:
            sl = current_price + sl_dist
            tp = current_price - (sl_dist * 2)

        sl_pips = sl_dist * 10000
        if "JPY" in symbol: sl_pips = sl_dist * 100

        pip_value = 10.0
        lots = risk_currency / (sl_pips * pip_value) if sl_pips > 0 else self.config.risk.min_lot_size

        return {
            "lots": max(self.config.risk.min_lot_size, round(lots, 2)),
            "sl": round(sl, 5),
            "tp": round(tp, 5)
        }

    def validate_trade(self, symbol: str, action: str, current_equity: float, current_price: float = 0.0, atr: float = 0.0, ignore_session: bool = False) -> Dict[str, Any]:
        if not ignore_session and not self.is_session_active():
            return {"safe": False, "reason": "Outside trading sessions"}
        if not self.is_news_safe():
            return {"safe": False, "reason": "High impact news pending"}
        if self.daily_trades >= 5:
            return {"safe": False, "reason": "Daily trade limit reached"}

        params = self.calculate_trade_params(current_equity, atr, symbol, action, current_price)

        return {
            "safe": True,
            "lots": params["lots"],
            "sl": params["sl"],
            "tp": params["tp"],
            "action": action,
            "symbol": symbol
        }
