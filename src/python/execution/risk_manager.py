import datetime
import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_RiskManager")

class RiskManager:
    """11000: Institutional Risk Vetting Engine."""
    def __init__(self, config):
        """
        11001: Initialize with config.
        Magic: 11001
        """
        self.config = config
        self.daily_trades = 0
        self.news_events: List[Dict[str, Any]] = []
        self.peak_equity = 0.0
        self.active_exposures: Dict[str, int] = {}
        self.load_news_from_file()

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        """
        11002: Load news.
        Magic: 11002
        """
        if os.path.exists(path):
            with open(path, "r") as f: self.news_events = json.load(f)

    def is_session_active(self) -> bool:
        """
        11003: Session check.
        Magic: 11003
        """
        now = datetime.datetime.now(datetime.UTC).time()
        l_start = datetime.time(8, 0); l_end = datetime.time(16, 0)
        n_start = datetime.time(13, 0); n_end = datetime.time(21, 0)
        return (l_start <= now <= l_end) or (n_start <= now <= n_end)

    def is_news_safe(self) -> bool:
        """
        11004: News safety check.
        Magic: 11004
        """
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                e_time = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                diff_min = abs((e_time - now).total_seconds()) / 60.0
                if diff_min <= 30.0:
                    if event.get("impact") == "High" or "NFP" in event.get("name", "") or "FOMC" in event.get("name", ""):
                        return False
            except: continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """
        11005: Position sizing.
        Magic: 11005
        """
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}

        risk_c = equity * (self.config.risk.risk_per_trade_pct / 100.0)
        sl_dist = atr * 2
        num_ticks = sl_dist / tick_size if tick_size > 0 else 0
        lots = risk_c / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size

        return {
            "lots": max(self.config.risk.min_lot_size, round(lots, 2)),
            "sl_pts": int(sl_dist / tick_size),
            "tp_pts": int((sl_dist * 2) / tick_size)
        }

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, spread: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """
        11006: Hardened 7-Layer Risk Stack validation.
        Magic: 11006
        """
        if not ignore_session and not self.is_session_active(): return {"safe": False, "reason": "OUTSIDE_TRADING_SESSION"}
        if not self.is_news_safe(): return {"safe": False, "reason": "HIGH_IMPACT_NEWS_BLACKOUT"}
        if self.daily_trades >= 5: return {"safe": False, "reason": "DAILY_TRADE_LIMIT"}

        if atr > 0 and spread > atr * 0.5: return {"safe": False, "reason": "SPREAD_BLOWOUT"}

        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct: return {"safe": False, "reason": f"DRAWDOWN_BREACH_{dd:.2f}%"}

        if symbol in self.active_exposures and self.active_exposures[symbol] != 0:
             return {"safe": False, "reason": "SYMBOL_ALREADY_EXPOSED"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
