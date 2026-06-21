import datetime
import json
import os
from typing import Dict, Any, List

class RiskManager:
    def __init__(self, config):
        """
        11001: Initialize the RiskManager with configuration and load scheduled news events.
        """
        self.config = config
        self.daily_trades = 0
        self.news_events: List[Dict[str, Any]] = []
        self.peak_equity = 0.0
        self.active_exposures: Dict[str, int] = {} # Net exposure per currency
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        """11002: Load scheduled news events."""
        if os.path.exists(path):
            with open(path, "r") as f: self.news_events = json.load(f)

    def is_session_active(self) -> bool:
        """11003: Active trading windows: 08:00-16:00 UTC and 13:00-21:00 UTC."""
        now = datetime.datetime.now(datetime.UTC).time()
        l_start = datetime.time(8, 0); l_end = datetime.time(16, 0)
        n_start = datetime.time(13, 0); n_end = datetime.time(21, 0)
        return (l_start <= now <= l_end) or (n_start <= now <= n_end)

    def is_news_safe(self) -> bool:
        """11004: News safety window check."""
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                e_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                if abs((e_time - now).total_seconds()) / 60.0 <= 30.0: return False
            except: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """11005: Volatility-based position sizing."""
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}
        risk_c = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_dist = atr * 2
        num_ticks = sl_dist / tick_size if tick_size > 0 else 0
        lots = risk_c / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size
        return {"lots": max(self.config.risk.min_lot_size, round(lots, 2)), "sl_pts": int(sl_dist / tick_size), "tp_pts": int((sl_dist * 2) / tick_size)}

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """11006: 7-Layer Risk Stack validation."""
        if not ignore_session and not self.is_session_active(): return {"safe": False, "reason": "OUTSIDE_TRADING_SESSION"}
        if not self.is_news_safe(): return {"safe": False, "reason": "HIGH_IMPACT_NEWS_WINDOW"}
        if self.daily_trades >= 5: return {"safe": False, "reason": "DAILY_TRADE_LIMIT_REACHED"}

        # 11007: Peak Equity & Drawdown Check
        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct: return {"safe": False, "reason": f"MAX_DRAWDOWN_BREACHED_{dd:.2f}%"}

        # 11008: Correlation & Exposure Check
        base, quote = symbol[:3], symbol[3:]
        dir_mult = 1 if action == "BUY" else -1
        if abs(self.active_exposures.get(base, 0) + dir_mult) > 2: return {"safe": False, "reason": f"MAX_EXPOSURE_EXCEEDED_{base}"}
        if abs(self.active_exposures.get(quote, 0) - dir_mult) > 2: return {"safe": False, "reason": f"MAX_EXPOSURE_EXCEEDED_{quote}"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
