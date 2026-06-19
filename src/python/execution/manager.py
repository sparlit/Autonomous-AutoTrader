import logging
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
            # Check for Partial TP at 1R
            entry_price = (trade["sl"] + trade["tp"]) / 2 # Simple approximation if not recorded
            # Better: use proper entry price from ledger if added

            # For simplicity, we calculate R relative to SL
            r_dist = abs(trade["sl"] - entry_price)
            curr_profit_r = abs(current_price - entry_price) / r_dist if r_dist > 0 else 0

            # Partial TP at 1R (50%)
            if curr_profit_r >= 1.0 and trade.get("status") == "OPEN" and not trade.get("partial_tp"):
                commands.append({
                    "t": "MGMT",
                    "tk": trade["ticket"],
                    "act": "CLOSE_PARTIAL",
                    "pct": 0.5
                })
                # Move to Breakeven
                commands.append({
                    "t": "MGMT",
                    "tk": trade["ticket"],
                    "act": "MODIFY_SL",
                    "sl": entry_price
                })
                # Update ledger state (need to add columns or use metadata)
                logger.info(f"Management: Partial TP and BE for ticket {trade['ticket']}")

            # Trailing Stop: 1.5x ATR
            if trade["action"] == "BUY":
                new_sl = current_price - (atr * 1.5)
                if new_sl > trade["sl"] + (atr * 0.5): # Only move if significant
                    commands.append({
                        "t": "MGMT",
                        "tk": trade["ticket"],
                        "act": "MODIFY_SL",
                        "sl": round(new_sl, 5)
                    })
            elif trade["action"] == "SELL":
                new_sl = current_price + (atr * 1.5)
                if new_sl < trade["sl"] - (atr * 0.5):
                    commands.append({
                        "t": "MGMT",
                        "tk": trade["ticket"],
                        "act": "MODIFY_SL",
                        "sl": round(new_sl, 5)
                    })

        return commands
