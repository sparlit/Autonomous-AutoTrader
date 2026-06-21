import logging
import datetime
from typing import Dict, Any, List
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    def __init__(self, ledger: TradeLedger):
        """Magic: 50001"""
        self.ledger = ledger
        self.magic = 50001

    async def monitor_and_manage(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        """Magic: 50002"""
        active_trades = await self.ledger.get_active_trades_db(symbol)
        commands = []

        for trade in active_trades:
            entry_price = trade.get("open_price")
            if entry_price is None:
                 # Standard pivot if exact open price is missing from ledger
                 entry_price = (trade["sl"] + trade["tp"]) / 2 if (trade["sl"] > 0 and trade["tp"] > 0) else current_price

            r_dist = abs(trade["sl"] - entry_price) if trade["sl"] > 0 else 0

            if trade["action"] == "BUY":
                curr_profit_r = (current_price - entry_price) / r_dist if r_dist > 0 else 0
                if curr_profit_r >= 1.0 and not trade.get("managed_1r"):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "CLOSE_PARTIAL", "pct": 0.5, "m_id": 50003})
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": entry_price, "m_id": 50004})
                    trade["managed_1r"] = True

                new_sl = current_price - (atr * 1.5)
                if new_sl > trade["sl"] + (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5), "m_id": 50005})

            elif trade["action"] == "SELL":
                curr_profit_r = (entry_price - current_price) / r_dist if r_dist > 0 else 0
                if curr_profit_r >= 1.0 and not trade.get("managed_1r"):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "CLOSE_PARTIAL", "pct": 0.5, "m_id": 50006})
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": entry_price, "m_id": 50007})
                    trade["managed_1r"] = True

                new_sl = current_price + (atr * 1.5)
                if new_sl < trade["sl"] - (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5), "m_id": 50008})

        return commands

    async def handle_closed_trade(self, ticket: int, exit_price: float, reason: str):
        """Magic: 50009"""
        logger.info(f"Finalizing trade {ticket}. Exit: {exit_price}, Reason: {reason}")
        await self.ledger.close_trade(ticket)
        return reason == "SL"
