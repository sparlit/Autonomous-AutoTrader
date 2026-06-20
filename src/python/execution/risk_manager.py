import datetime
import json
import os
from typing import Dict, Any, List

class RiskManager:
    def __init__(self, config):
        """
        Initialize the RiskManager with configuration and load scheduled news events.

        Parameters:
		config: Configuration object containing risk parameters.
        """
        self.config = config
        self.daily_trades = 0
        self.news_events: List[Dict[str, Any]] = []
        self.peak_equity = 0.0
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        """
        Load scheduled news events from a JSON file.

        If the specified file does not exist, self.news_events remains unchanged.

        Parameters:
		path (str): Path to the JSON file containing scheduled news events. Defaults to "config/news_schedule.json".
        """
        if os.path.exists(path):
            with open(path, "r") as f: self.news_events = json.load(f)

    def is_session_active(self) -> bool:
        """
        Determine if the current UTC time falls within active trading sessions.

        The active trading windows are 08:00-16:00 UTC and 13:00-21:00 UTC.

        Returns:
            `true` if current time is within either window, `false` otherwise.
        """
        now = datetime.datetime.now(datetime.UTC).time()
        l_start = datetime.time(8, 0); l_end = datetime.time(16, 0)
        n_start = datetime.time(13, 0); n_end = datetime.time(21, 0)
        return (l_start <= now <= l_end) or (n_start <= now <= n_end)

    def is_news_safe(self) -> bool:
        """
        Determine if trading is safe relative to scheduled news events.

        Returns:
            bool: `true` if no scheduled news events are within 30 minutes of the current time, `false` otherwise.
        """
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                e_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                if abs((e_time - now).total_seconds()) / 60.0 <= 30.0: return False
            except: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """
        Calculate position size and risk points based on equity and volatility.

        Parameters:
            atr (float): Average True Range; returns minimum position if zero or negative.
            tick_val (float): Monetary value of a single tick.
            tick_size (float): Size of one tick in price units.

        Returns:
            dict: Contains "lots" (position quantity at or above minimum), "sl_pts" (stop-loss distance in points), and "tp_pts" (take-profit distance in points).
        """
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}
        risk_c = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_dist = atr * 2
        num_ticks = sl_dist / tick_size if tick_size > 0 else 0
        lots = risk_c / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size
        return {"lots": max(self.config.risk.min_lot_size, round(lots, 2)), "sl_pts": int(sl_dist / tick_size), "tp_pts": int((sl_dist * 2) / tick_size)}

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """
        Validate a trade against risk constraints and compute trade parameters if constraints are met.

        Checks session activity, news event proximity, daily trade limits, and drawdown thresholds.
        Returns trade approval status and computed parameters (position size, stops, targets) if approved.

        Parameters:
		current_equity (float): Current account equity.
		atr (float): Average True Range for volatility-based risk calculation.
		tick_val (float): Point value per tick.
		tick_size (float): Minimum price increment.
		ignore_session (bool): If True, skip the session time validation.

        Returns:
		result (dict): Contains 'safe' (bool). If True, includes 'lots', 'sl_pts', 'tp_pts', 'action', 'symbol'.
			If False, includes 'reason' explaining the rejection cause.
        """
        if not ignore_session and not self.is_session_active(): return {"safe": False, "reason": "Outside session"}
        if not self.is_news_safe(): return {"safe": False, "reason": "News pending"}
        if self.daily_trades >= 5: return {"safe": False, "reason": "Limit reached"}
        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct: return {"safe": False, "reason": f"DD reached ({dd:.2f}%)"}
        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
