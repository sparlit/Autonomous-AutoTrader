import logging
import datetime
from typing import Dict, Any, List
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    def __init__(self, ledger: TradeLedger):
        self.ledger = ledger

    async def monitor_and_manage(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        active_trades = await self.ledger.get_active_trades(symbol)
        commands = []

        for trade in active_trades:
            entry_price = (trade["sl"] + trade["tp"]) / 2 # Approx
            r_dist = abs(trade["sl"] - entry_price)
            curr_profit_r = abs(current_price - entry_price) / r_dist if r_dist > 0 else 0

            if curr_profit_r >= 1.0 and trade.get("status") == "OPEN" and not trade.get("partial_tp"):
                commands.append({
                    "t": "MGMT", "tk": trade["ticket"], "act": "CLOSE_PARTIAL", "pct": 0.5
                })
                commands.append({
                    "t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": entry_price
                })
                logger.info(f"Management: Partial TP and BE for ticket {trade['ticket']}")

            if trade["action"] == "BUY":
                new_sl = current_price - (atr * 1.5)
                if new_sl > trade["sl"] + (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5)})
            elif trade["action"] == "SELL":
                new_sl = current_price + (atr * 1.5)
                if new_sl < trade["sl"] - (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5)})

        return commands

    async def handle_closed_trade(self, ticket: int, exit_price: float, reason: str):
        """Update ledger and check for SL hits to trigger cooldown."""
        # This would be called from SYNC or TRADE_TRANSACTION (Week 3/4)
        # For now, we update the ledger
        await self.ledger.close_trade(ticket)
        # Logic for cooldown return to coordinator
        return True if reason == "SL" else False
