import datetime
from typing import Dict, Any

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_trades = 0
        self.last_trade_time = None

    def is_session_active(self) -> bool:
        """Check if London or New York session is active."""
        # For testing purposes, we can allow a bypass or just return True if mocked
        # In production, this uses UTC time
        now = datetime.datetime.now(datetime.UTC).time()
        london_start = datetime.time(8, 0)
        london_end = datetime.time(16, 0)
        ny_start = datetime.time(13, 0)
        ny_end = datetime.time(21, 0)

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
            "action": action,
            "symbol": symbol
        }
