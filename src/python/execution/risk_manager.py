import datetime
import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_RiskManager")

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
        """
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.news_events = json.load(f)
                logger.info(f"Loaded {len(self.news_events)} news events from {path}")
            except Exception as e:
                logger.error(f"Failed to load news: {e}")

    def is_session_active(self) -> bool:
        """
        Determine if the current UTC time falls within active trading sessions.
        """
        now = datetime.datetime.now(datetime.UTC).time()
        # London: 08:00-16:00, NY: 13:00-21:00
        l_start = datetime.time(8, 0); l_end = datetime.time(16, 0)
        n_start = datetime.time(13, 0); n_end = datetime.time(21, 0)
        return (l_start <= now <= l_end) or (n_start <= now <= n_end)

    def is_news_safe(self) -> bool:
        """
        Determine if trading is safe relative to scheduled news events.
        Enforces a 30-minute window around high-impact news.
        """
        now = datetime.datetime.now(datetime.UTC)
        for event in self.news_events:
            try:
                # Expecting ISO format like 2024-06-19T13:30:00Z
                e_time_str = event["time"].replace("Z", "+00:00")
                e_time = datetime.datetime.fromisoformat(e_time_str)
                # Convert both to offset-aware if they aren't
                if e_time.tzinfo is None: e_time = e_time.replace(tzinfo=datetime.UTC)

                diff_mins = abs((e_time - now).total_seconds()) / 60.0
                if diff_mins <= 30.0 and event.get("impact") == "HIGH":
                    logger.warning(f"VETO: High-impact news '{event.get('event')}' in {diff_mins:.1f} mins.")
                    return False
            except Exception as e:
                logger.error(f"Error parsing news time: {e}")
                continue
        return True

    def calculate_trade_params(self, equity: float, atr: float, symbol: str, action: str, tick_val: float = 10.0, tick_size: float = 0.0001) -> Dict[str, Any]:
        """
        Calculate position size and risk points based on equity and volatility.
        """
        if atr <= 0: return {"lots": self.config.risk.min_lot_size, "sl_pts": 0, "tp_pts": 0}

        # Risk amount in currency
        risk_amount = equity * (self.config.risk.risk_per_trade_pct / 100.0)

        # Stop loss distance: 2.0x ATR
        sl_dist = atr * 2.0

        # Convert SL distance to points/ticks
        num_ticks = sl_dist / tick_size if tick_size > 0 else 0

        # Position sizing: Risk / (Ticks * TickValue)
        # TickValue is usually for 1.0 lot
        lots = risk_amount / (num_ticks * tick_val) if num_ticks > 0 and tick_val > 0 else self.config.risk.min_lot_size

        # Final parameters
        final_lots = max(self.config.risk.min_lot_size, round(lots, 2))
        sl_pts = int(sl_dist / tick_size) if tick_size > 0 else 0
        tp_pts = int((sl_dist * 1.5) / tick_size) if tick_size > 0 else 0 # 1.5R target

        return {"lots": final_lots, "sl_pts": sl_pts, "tp_pts": tp_pts}

    def validate_trade(self, symbol: str, action: str, current_equity: float, atr: float = 0.0, tick_val: float = 10.0, tick_size: float = 0.0001, ignore_session: bool = False) -> Dict[str, Any]:
        """
        Validate a trade against risk constraints and compute trade parameters.
        """
        if not ignore_session and not self.is_session_active():
            return {"safe": False, "reason": "Outside session"}

        if not self.is_news_safe():
            return {"safe": False, "reason": "News pending"}

        if self.daily_trades >= 5:
            return {"safe": False, "reason": "Daily limit reached"}

        if self.peak_equity > 0:
            dd = (self.peak_equity - current_equity) / self.peak_equity * 100.0
            if dd > self.config.risk.max_drawdown_pct:
                return {"safe": False, "reason": f"Max DD reached ({dd:.2f}%)"}

        p = self.calculate_trade_params(current_equity, atr, symbol, action, tick_val, tick_size)
        return {
            "safe": True,
            "lots": p["lots"],
            "sl_pts": p["sl_pts"],
            "tp_pts": p["tp_pts"],
            "action": action,
            "symbol": symbol
        }
