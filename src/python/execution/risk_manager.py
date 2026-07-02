import datetime
import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_RiskManager")

class RiskManager:
    """11000: Institutional Risk Vetting Engine (V3.3.0-ASCENDANT)."""
    def __init__(self, config, ipc=None):
        self.config = config
        self.ipc = ipc
        self._daily_trades = 0
        self._peak_equity = 0.0
        self._active_exposures: Dict[str, int] = {}
        self.news_events: List[Dict[str, Any]] = []
        self.load_news_from_file()

    @property
    def daily_trades(self) -> int:
        if self.ipc: return self.ipc.get_state("risk:daily_trades", 0)
        return self._daily_trades

    @daily_trades.setter
    def daily_trades(self, value: int):
        if self.ipc: self.ipc.set_state("risk:daily_trades", value)
        else: self._daily_trades = value

    @property
    def peak_equity(self) -> float:
        if self.ipc: return self.ipc.get_state("risk:peak_equity", 0.0)
        return self._peak_equity

    @peak_equity.setter
    def peak_equity(self, value: float):
        if self.ipc: self.ipc.set_state("risk:peak_equity", value)
        else: self._peak_equity = value

    @property
    def active_exposures(self) -> Dict[str, int]:
        if self.ipc: return self.ipc.get_state("risk:active_exposures", {})
        return self._active_exposures

    @active_exposures.setter
    def active_exposures(self, value: Dict[str, int]):
        if self.ipc: self.ipc.set_state("risk:active_exposures", value)
        else: self._active_exposures = value

    def increment_trade_count(self, symbol: str):
        self.daily_trades += 1
        exposures = self.active_exposures
        exposures[symbol] = exposures.get(symbol, 0) + 1
        self.active_exposures = exposures

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        if os.path.exists(path):
            try:
                with open(path, "r") as f: self.news_events = json.load(f)
            except: logger.warning("Failed to load news")

    def is_session_active(self, symbol: str = "GLOBAL") -> bool:
        now_utc = datetime.datetime.now(datetime.UTC)
        weekday = now_utc.weekday()
        time_utc = now_utc.time()
        if symbol == "GLOBAL" or any(c in symbol.upper() for c in ["BTC", "ETH"]): return True
        if weekday == 5: return False
        if weekday == 6 and time_utc < datetime.time(21, 0): return False
        if weekday == 4 and time_utc > datetime.time(22, 0): return False
        return True

    def is_news_safe(self) -> bool:
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                e_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                if abs((e_time - now).total_seconds()) / 60.0 <= 30.0:
                    if event.get("impact") == "High": return False
            except: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """
        11005: Strict Lot Sizing & Initial RR (1:1).
        Rule: Maximum lot size for initial trades will be 0.01 lots only.
        """
        lots = 0.01
        if atr <= 0: return {"lots": lots, "sl_pts": 0, "tp_pts": 0}

        # Initial SL at 2*ATR
        sl_dist = atr * 2
        sl_pts = int(sl_dist / tick_size) if tick_size > 0 else 100

        # Rule: Initial TP at 1:1 RR
        tp_pts = sl_pts

        return {"lots": lots, "sl_pts": sl_pts, "tp_pts": tp_pts}

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, spread: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        if not ignore_session and not self.is_session_active(symbol): return {"safe": False, "reason": "SESSION_CLOSED"}
        if not self.is_news_safe(): return {"safe": False, "reason": "NEWS_BLACKOUT"}
        if self.daily_trades >= 50: return {"safe": False, "reason": "DAILY_LIMIT"}
        if atr > 0 and spread > atr * 0.5: return {"safe": False, "reason": "SPREAD_HIGH"}

        # Rule: Scaling allowed if prev trades in profit (handled in Orchestrator/Manager)
        # RiskManager just ensures we don't blow up.
        if self.active_exposures.get(symbol, 0) >= 10: return {"safe": False, "reason": "MAX_LAYERS"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
