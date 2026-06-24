import logging
import time
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """
    15001: Active trade lifecycle controller (Master Pro Edition).
    Handles Partial TP @ 1R, Breakeven, and Trailing Stops.
    """
    def __init__(self, ledger: TradeLedger):
        self.ledger = ledger

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float) -> List[Dict[str, Any]]:
        """
        15002: Advanced lifecycle management for open positions.
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        if not active_trades: return []

        management_orders = []

        for trade in active_trades:
            ticket = trade["ticket"]
            entry = trade.get("entry_price", 0.0)
            if entry == 0 or ticket == 0: continue

            action = trade["action"]
            sl = trade.get("sl_price", 0.0)
            tp = trade.get("tp_price", 0.0)

            current_price = bid if action == "BUY" else ask

            # Risk Distance for 1R Target
            risk_dist = abs(entry - sl)
            if risk_dist == 0: continue

            target_1r = entry + risk_dist if action == "BUY" else entry - risk_dist

            # 1. Partial TP @ 1R (50% close)
            if not trade.get("partial_tp_hit", False):
                hit = (action == "BUY" and current_price >= target_1r) or (action == "SELL" and current_price <= target_1r)
                if hit:
                    logger.info(f"Management: Partial TP Target 1R hit for {symbol} Ticket {ticket}")
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "CLOSE_PARTIAL",
                        "tk": ticket,
                        "s": symbol,
                        "pct": 0.5,
                        "reason": "PARTIAL_TP_1R"
                    })
                    await self.ledger.set_partial_hit(ticket)

            # 2. Breakeven move after 1.5R
            target_15r = entry + 1.5 * risk_dist if action == "BUY" else entry - 1.5 * risk_dist
            hit_15r = (action == "BUY" and current_price >= target_15r) or (action == "SELL" and current_price <= target_15r)

            if hit_15r:
                # Move SL to entry
                if (action == "BUY" and sl < entry) or (action == "SELL" and sl > entry):
                    logger.info(f"Management: Moving to Breakeven for {symbol} Ticket {ticket}")
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "MODIFY_SL",
                        "tk": ticket,
                        "s": symbol,
                        "sl": entry,
                        "reason": "BREAKEVEN_1.5R"
                    })

            # 3. Trailing Stop (Dynamic 2x ATR trailing)
            if action == "BUY":
                potential_sl = current_price - 2 * atr
                if potential_sl > sl and potential_sl > entry: # Only trail once in profit
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "MODIFY_SL",
                        "tk": ticket,
                        "s": symbol,
                        "sl": potential_sl,
                        "reason": "TRAILING_ATR"
                    })
            else:
                potential_sl = current_price + 2 * atr
                if potential_sl < sl and potential_sl < entry:
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "MODIFY_SL",
                        "tk": ticket,
                        "s": symbol,
                        "sl": potential_sl,
                        "reason": "TRAILING_ATR"
                    })

        return management_orders
