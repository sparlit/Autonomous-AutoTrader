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

    async def monitor_and_manage(self, symbol: str, current_price: float, atr: float) -> Optional[List[Dict[str, Any]]]:
        """
        15002: Advanced lifecycle management for open positions.
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        if not active_trades: return None

        management_orders = []

        for trade in active_trades:
            ticket = trade["ticket"]
            entry = trade.get("entry_price", 0.0)
            if entry == 0: continue

            action = trade["action"]
            sl = trade.get("sl_price", 0.0)
            tp = trade.get("tp_price", 0.0)

            # 1. Partial TP @ 1R (50% close)
            # 1R distance = entry - initial_sl
            risk_dist = abs(entry - sl)
            target_1r = entry + risk_dist if action == "BUY" else entry - risk_dist

            if not trade.get("partial_tp_hit", False):
                if (action == "BUY" and current_price >= target_1r) or (action == "SELL" and current_price <= target_1r):
                    management_orders.append({
                        "act": "CLOSE_PARTIAL",
                        "tk": ticket,
                        "pct": 0.5,
                        "reason": "PARTIAL_TP_1R"
                    })
                    # Note: In real system, we'd update DB here or after ACK

            # 2. Breakeven move after 1.5R
            target_15r = entry + 1.5 * risk_dist if action == "BUY" else entry - 1.5 * risk_dist
            if (action == "BUY" and current_price >= target_15r) or (action == "SELL" and current_price <= target_15r):
                # Move SL to entry + small buffer
                new_sl = entry + 2 * atr if action == "BUY" else entry - 2 * atr # Wait, that's trailing. BE is entry.
                new_sl = entry
                if sl != new_sl:
                    management_orders.append({
                        "act": "MODIFY_SL",
                        "tk": ticket,
                        "sl": new_sl,
                        "reason": "BREAKEVEN_1.5R"
                    })

            # 3. Trailing Stop (Dynamic ATR trailing)
            if action == "BUY":
                potential_sl = current_price - 2 * atr
                if potential_sl > sl:
                     management_orders.append({
                        "act": "MODIFY_SL",
                        "tk": ticket,
                        "sl": potential_sl,
                        "reason": "TRAILING_ATR"
                    })
            else:
                potential_sl = current_price + 2 * atr
                if potential_sl < sl:
                     management_orders.append({
                        "act": "MODIFY_SL",
                        "tk": ticket,
                        "sl": potential_sl,
                        "reason": "TRAILING_ATR"
                    })

        return management_orders
