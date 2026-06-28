import logging
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """10500: Institutional Position Lifecycle Management."""
    def __init__(self, ledger: TradeLedger, risk_manager: RiskManager):
        """10501: Initialize PositionManager."""
        self.ledger = ledger
        self.risk_manager = risk_manager

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float, smc_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """10505: Master management entry point."""
        current_price = (bid + ask) / 2
        return await self.manage_open_positions(symbol, current_price, atr, smc_data)

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float, smc_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
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

            # 10504: Hybrid ATR-SMC Trailing Stop
            # Magic: 10504
            if atr > 0:
                potential_sl = 0.0
                reason = "TRAILING_ATR"

                if action == "BUY":
                    # ATR Base
                    potential_sl = current_price - 2 * atr
                    # SMC Snap-to-Structure
                    if smc_data and smc_data.get("swing_l"):
                        swing_l = smc_data["swing_l"]
                        if swing_l > potential_sl and swing_l < current_price:
                            potential_sl = swing_l
                            reason = "TRAILING_SMC_SWING_L"

                    if potential_sl > sl and potential_sl < current_price:
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": ticket,
                            "s": symbol, "sl": potential_sl, "reason": reason
                        })
                else:
                    # ATR Base
                    potential_sl = current_price + 2 * atr
                    # SMC Snap-to-Structure
                    if smc_data and smc_data.get("swing_h"):
                        swing_h = smc_data["swing_h"]
                        if swing_h < potential_sl and swing_h > current_price:
                            potential_sl = swing_h
                            reason = "TRAILING_SMC_SWING_H"

                    if potential_sl < sl and potential_sl > current_price:
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": ticket,
                            "s": symbol, "sl": potential_sl, "reason": reason
                        })

        return management_orders
