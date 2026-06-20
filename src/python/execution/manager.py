import logging
import datetime
from typing import Dict, Any, List
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    def __init__(self, ledger: TradeLedger):
        self.ledger = ledger
        self.magic = 5001

    async def monitor_and_manage(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        """
        Full state-machine position management.
        Magic: 5002
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        commands = []

        for trade in active_trades:
            entry_price = trade.get("open_price", (trade["sl"] + trade["tp"]) / 2)
            r_dist = abs(trade["sl"] - entry_price)

            if trade["action"] == "BUY":
                curr_profit_r = (current_price - entry_price) / r_dist if r_dist > 0 else 0
                if curr_profit_r >= 1.0 and not trade.get("managed_1r"):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "CLOSE_PARTIAL", "pct": 0.5, "m_id": 5003})
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": entry_price, "m_id": 5004})
                    trade["managed_1r"] = True

                new_sl = current_price - (atr * 1.5)
                if new_sl > trade["sl"] + (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5), "m_id": 5005})

            elif trade["action"] == "SELL":
                curr_profit_r = (entry_price - current_price) / r_dist if r_dist > 0 else 0
                if curr_profit_r >= 1.0 and not trade.get("managed_1r"):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "CLOSE_PARTIAL", "pct": 0.5, "m_id": 5006})
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": entry_price, "m_id": 5007})
                    trade["managed_1r"] = True

                new_sl = current_price + (atr * 1.5)
                if new_sl < trade["sl"] - (atr * 0.5):
                    commands.append({"t": "MGMT", "tk": trade["ticket"], "act": "MODIFY_SL", "sl": round(new_sl, 5), "m_id": 5008})

        return commands

    async def handle_closed_trade(self, ticket: int, exit_price: float, reason: str):
        """
        Record final trade outcome and perform cleanup.
        Magic: 5009
        """
        logger.info(f"Finalizing trade {ticket}. Exit: {exit_price}, Reason: {reason}")
        await self.ledger.close_trade(ticket)
        return reason == "SL"
