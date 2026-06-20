import logging
import datetime
from typing import Dict, Any, List
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    def __init__(self, ledger: TradeLedger):
        """
        Initialize the PositionManager with a trade ledger.
        
        Parameters:
            ledger (TradeLedger): The trade ledger instance for managing open positions.
        """
        self.ledger = ledger

    async def monitor_and_manage(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        """
        Generate trade management commands for active trades based on current price movement and ATR.
        
        Evaluates each active trade and generates commands to close 50% of the position and adjust the stop-loss to breakeven when profit reaches 1.0 R-multiple. Also applies ATR-based trailing stop-loss adjustments for BUY and SELL positions.
        
        Parameters:
            atr (float): The Average True Range value used for stop-loss calculations.
        
        Returns:
            List[Dict[str, Any]]: Trade management commands.
        """
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
        """
        Close a trade in the ledger and indicate whether it was stopped out.
        
        Parameters:
        	ticket (int): The trade ticket identifier
        	exit_price (float): The price at which the trade closed
        	reason (str): The reason for closure
        
        Returns:
        	bool: `True` if the trade was closed due to a stop-loss, `False` otherwise.
        """
        # This would be called from SYNC or TRADE_TRANSACTION (Week 3/4)
        # For now, we update the ledger
        await self.ledger.close_trade(ticket)
        # Logic for cooldown return to coordinator
        return True if reason == "SL" else False
