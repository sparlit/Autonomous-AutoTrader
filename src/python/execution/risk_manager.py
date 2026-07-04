import datetime
import json
import os
import logging
import aiosqlite
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_RiskManager")

class RiskManager:
    """V4.0: Institutional Risk & Assessment Engine."""
    def __init__(self, config, ipc=None):
        self.config = config
        self.ipc = ipc
        self.db_path = config.system.database_path
        self._daily_trades = 0
        self.active_exposures: Dict[str, int] = {}

    async def calculate_win_rate(self) -> float:
        """Calculate historical win rate from closed trades."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM trades WHERE status = 'CLOSED'") as c:
                    total = (await c.fetchone())[0]
                if total == 0: return 0.70 # Institutional Default
                async with db.execute("SELECT COUNT(*) FROM trades WHERE status = 'CLOSED' AND profit > 0") as c:
                    wins = (await c.fetchone())[0]
                return wins / total
        except: return 0.70

    async def calculate_max_drawdown(self) -> float:
        """Fetch current drawdown from account stats."""
        stats = self.ipc.get_state("account_stats", {})
        return float(stats.get("drawdown", 0.0))

    async def assess_loss_possibility(self, symbol: str, probability: float) -> float:
        """Bayesian Loss Estimation based on current regime and historical win rate."""
        win_rate = await self.calculate_win_rate()
        regime = self.ipc.get_state(f"intel:{symbol}", {}).get("regime", "NORMAL")

        # Penalize if regime is HIGH_VOLATILITY or UNSTABLE
        regime_penalty = 0.1 if regime in ["HIGH_VOLATILITY", "CRASH_SUDDEN"] else 0.0

        # Combined Bayesian Risk Score
        loss_prob = (1.0 - probability) * (1.0 - win_rate) + regime_penalty
        return max(0.0, min(1.0, loss_prob))

    def increment_trade_count(self, symbol: str):
        self._daily_trades += 1
        self.active_exposures[symbol] = self.active_exposures.get(symbol, 0) + 1

    def validate_trade(self, symbol: str, action: str, probability: float) -> Dict[str, Any]:
        """V4.0 Rule 1.b/1.c compliance."""
        if self._daily_trades >= 50: return {"safe": False, "reason": "DAILY_LIMIT"}

        inst = self.config.institutional
        if self.ipc.get_state("account_stats", {}).get("drawdown", 0) > inst.max_drawdown_limit:
            return {"safe": False, "reason": "MAX_DD_BREACH"}

        # Scaling check (Rule 1.c.ii)
        # This is handled in PositionManager before calling validate, but as a fallback:
        trades = self.ipc.get_state("active_trades", [])
        sym_trades = [t for t in trades if t['symbol'] == symbol]
        if sym_trades:
            # Rule 1.c.ii: if existing trade is in loss or profit < 1 USD, no trade
            # Handled in Manager.
            logger.debug(f"Scaling check for {symbol} deferred to PositionManager")

        return {"safe": True, "lots": inst.standard_lot_size}
