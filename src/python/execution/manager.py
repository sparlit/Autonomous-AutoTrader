import logging
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """10500: Institutional Position Lifecycle Management."""
    def __init__(self, ledger: TradeLedger):
        self.ledger = ledger

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        """
        10501: Automated trade management: Partial Close and Breakeven logic.
        Magic: 10501
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        management_orders = []

        for trade in active_trades:
            ticket = trade['ticket']
            entry = trade['entry_price']
            sl = trade['sl_price']
            tp = trade['tp_price']
            action = trade['action']

            # 10502: Partial Close at 1R (50% position reduction)
            # Magic: 10502
            if trade['partial_tp_hit'] == 0:
                dist_to_tp = abs(tp - entry)
                one_r_level = entry + (dist_to_tp * 0.5) if action == "BUY" else entry - (dist_to_tp * 0.5)

                is_hit = (action == "BUY" and current_price >= one_r_level) or (action == "SELL" and current_price <= one_r_level)
                if is_hit:
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "PARTIAL_CLOSE",
                        "tk": ticket,
                        "s": symbol,
                        "vol": trade['lots'] * 0.5,
                        "reason": "1R_PARTIAL"
                    })
                    await self.ledger.set_partial_hit(ticket)

            # 10503: Breakeven adjustment after 1R
            # Magic: 10503
            if trade['partial_tp_hit'] == 1:
                if (action == "BUY" and sl < entry) or (action == "SELL" and sl > entry):
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "MODIFY_SL",
                        "tk": ticket,
                        "s": symbol,
                        "sl": entry,
                        "reason": "BREAKEVEN_PROTECTION"
                    })

            # 10504: Trailing Stop (ATR-based)
            # Magic: 10504
            if action == "BUY":
                potential_sl = current_price - 2 * atr
                if potential_sl > sl and potential_sl < current_price:
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
                if potential_sl < sl and potential_sl > current_price:
                    management_orders.append({
                        "type": "EXECUTION_ORDER",
                        "t": "MODIFY_SL",
                        "tk": ticket,
                        "s": symbol,
                        "sl": potential_sl,
                        "reason": "TRAILING_ATR"
                    })

        return management_orders
