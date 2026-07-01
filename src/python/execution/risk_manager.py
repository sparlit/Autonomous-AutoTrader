import datetime
import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_RiskManager")

class RiskManager:
    """11000: Institutional Risk Vetting Engine."""
    def __init__(self, config, ipc=None):
        """
        11001: Initialize with config and optional IPC for shared state.
        Magic: 11001
        """
        self.config = config
        self.ipc = ipc
        self._daily_trades = 0
        self._peak_equity = 0.0
        self._active_exposures: Dict[str, int] = {}
        self.news_events: List[Dict[str, Any]] = []
        self.load_news_from_file()

    @property
    def daily_trades(self) -> int:
        if self.ipc:
            return self.ipc.get_state("risk:daily_trades", 0)
        return self._daily_trades

    @daily_trades.setter
    def daily_trades(self, value: int):
        if self.ipc:
            self.ipc.set_state("risk:daily_trades", value)
        else:
            self._daily_trades = value

    @property
    def peak_equity(self) -> float:
        if self.ipc:
            return self.ipc.get_state("risk:peak_equity", 0.0)
        return self._peak_equity

    @peak_equity.setter
    def peak_equity(self, value: float):
        if self.ipc:
            self.ipc.set_state("risk:peak_equity", value)
        else:
            self._peak_equity = value

    @property
    def active_exposures(self) -> Dict[str, int]:
        if self.ipc:
            return self.ipc.get_state("risk:active_exposures", {})
        return self._active_exposures

    @active_exposures.setter
    def active_exposures(self, value: Dict[str, int]):
        if self.ipc:
            self.ipc.set_state("risk:active_exposures", value)
        else:
            self._active_exposures = value

    def increment_trade_count(self, symbol: str):
        """11015: Synchronized trade increment."""
        self.daily_trades += 1
        exposures = self.active_exposures
        exposures[symbol] = exposures.get(symbol, 0) + 1
        self.active_exposures = exposures
        logger.info(f"Risk state updated: Daily Trades={self.daily_trades}, {symbol} Exposure={exposures[symbol]}")

    def load_news_from_file(self, path: str = "config/news_schedule.json"):
        """
        11002: Load news.
        Magic: 11002
        """
        if os.path.exists(path):
            try:
                with open(path, "r") as f: self.news_events = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load news: {e}")

    def is_session_active(self, symbol: str = "GLOBAL") -> bool:
        """
        11003: Multi-Asset Session Vetting (24/7 Crypto, 24/5 FX/Commodities).
        Magic: 11003
        """
        now_utc = datetime.datetime.now(datetime.UTC)
        weekday = now_utc.weekday() # 0=Mon, 6=Sun
        time_utc = now_utc.time()

        if symbol == "GLOBAL" or any(c in symbol.upper() for c in ["BTC", "ETH", "SOL", "BNB", "XRP"]):
            return True

        if weekday == 5: # Saturday
            return False
        if weekday == 6 and time_utc < datetime.time(21, 0): # Sunday before Sydney/Tokyo
            return False
        if weekday == 4 and time_utc > datetime.time(22, 0): # Friday after NY close
            return False

        return True

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

    def calculate_institutional_params(self, equity: float, atr: float, symbol: str, action: str,
                                     probability: float = 0.5, confluence: int = 0,
                                     regime: str = "NORMAL", tick_val: float = 10.0,
                                     tick_size: float = 0.0001) -> Dict[str, Any]:
        """
        11010: Institutional Alpha Position Sizing & SL/TP Calibration.
        """
        base_params = self.calculate_trade_params(equity, atr, symbol, action, tick_val, tick_size)
        regime_mult = 1.2 if "TRENDING_FAST" in regime else (1.0 if "TRENDING" in regime else 0.8)
        prob_mult = probability / 0.70
        conf_mult = 1.0 + (confluence - 3) * 0.1 if confluence >= 3 else 0.7
        final_lots = base_params["lots"] * regime_mult * prob_mult * conf_mult
        tp_mult = 1.0 + (probability - 0.7) * 2.0

        return {
            "lots": max(self.config.risk.min_lot_size, round(final_lots, 2)),
            "sl_pts": base_params["sl_pts"],
            "tp_pts": int(base_params["tp_pts"] * max(1.0, tp_mult))
        }

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, spread: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """
        11006: Hardened 7-Layer Risk Stack validation.
        Magic: 11006
        """
        if not ignore_session and not self.is_session_active(symbol): return {"safe": False, "reason": "OUTSIDE_TRADING_SESSION"}
        if not self.is_news_safe(): return {"safe": False, "reason": "HIGH_IMPACT_NEWS_BLACKOUT"}

        # Shared state check
        if self.daily_trades >= 5: return {"safe": False, "reason": f"DAILY_TRADE_LIMIT_REACHED_{self.daily_trades}"}

        if atr > 0 and spread > atr * 0.5: return {"safe": False, "reason": "SPREAD_BLOWOUT"}

        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct: return {"safe": False, "reason": f"DRAWDOWN_BREACH_{dd:.2f}%"}

        if symbol in self.active_exposures and self.active_exposures[symbol] != 0:
             return {"safe": False, "reason": "SYMBOL_ALREADY_EXPOSED"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {"safe": True, "lots": p["lots"], "sl_pts": p["sl_pts"], "tp_pts": p["tp_pts"], "action": action, "symbol": symbol}
