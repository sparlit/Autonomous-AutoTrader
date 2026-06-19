import datetime
from typing import Dict, Any, List

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_trades = 0
        self.last_trade_time = None
        self.news_events: List[Dict[str, Any]] = []

    def load_news_schedule(self, events: List[Dict[str, Any]]):
        """Load upcoming high-impact news events."""
        self.news_events = events

    def is_session_active(self) -> bool:
        now = datetime.datetime.now(datetime.UTC).time()
        london_start = datetime.time(8, 0)
        london_end = datetime.time(16, 0)
        ny_start = datetime.time(13, 0)
        ny_end = datetime.time(21, 0)
        return (london_start <= now <= london_end) or (ny_start <= now <= ny_end)

    def is_news_safe(self) -> bool:
        """Check if we are within 30 minutes of a high-impact news event."""
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            event_time = datetime.datetime.fromisoformat(event["time"])
            diff = abs((event_time - now).total_seconds()) / 60.0
            if diff <= 30.0:
                return False
        return True

    def calculate_lots(self, equity: float, atr: float, symbol: str) -> float:
        if atr <= 0: return self.config.risk.min_lot_size
        risk_currency = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_pips = (atr * 2) * 10000
        if "JPY" in symbol: sl_pips = (atr * 2) * 100
        pip_value = 10.0
        if sl_pips == 0: return self.config.risk.min_lot_size
        lots = risk_currency / (sl_pips * pip_value)
        return max(self.config.risk.min_lot_size, round(lots, 2))

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, ignore_session: bool = False) -> Dict[str, Any]:
        if not ignore_session and not self.is_session_active():
            return {"safe": False, "reason": "Outside trading sessions"}

        if not self.is_news_safe():
            return {"safe": False, "reason": "High impact news pending"}

        if self.daily_trades >= 5:
            return {"safe": False, "reason": "Daily trade limit reached"}

        lots = self.calculate_lots(current_equity, atr, symbol)

        return {
            "safe": True,
            "lots": lots,
            "action": action,
            "symbol": symbol
        }
