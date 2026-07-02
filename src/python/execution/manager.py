import logging
import time
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """10500: Institutional Position Lifecycle Management."""
    def __init__(self, ledger: TradeLedger, risk_manager: RiskManager):
        self.ledger = ledger
        self.risk_manager = risk_manager

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float, smc_data: Optional[Dict[str, Any]] = None, mtf_trends: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """10505: Master management entry point with Scaling logic."""
        current_price = (bid + ask) / 2
        orders = await self.manage_open_positions(symbol, current_price, atr, smc_data)

        # Rule: Scaling - Add 0.01 lots if trade is in profit and trend is in favor
        active_trades = await self.ledger.get_active_trades_db(symbol)
        if len(active_trades) == 1 and mtf_trends:
            trade = active_trades[0]
            profit_points = (current_price - trade["entry_price"]) if trade["action"] == "BUY" else (trade["entry_price"] - current_price)

            # If in profit and MTF trend aligns
            if profit_points > 0:
                trend = "BULLISH" if trade["action"] == "BUY" else "BEARISH"
                # Check H1 and H4 for scaling trend alignment
                if mtf_trends.get("h1") == trend and mtf_trends.get("h4") == trend:
                    # Trigger scaling via signal
                    orders.append({
                        "type": "PROBABILISTIC_SIGNAL",
                        "symbol": symbol,
                        "action": trade["action"],
                        "probability": 0.85,
                        "reason": "SCALING_IN_TREND",
                        "atr": atr,
                        "scaling": True
                    })

        return orders

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float, smc_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        10501: Risk-to-Reward (RR) Based Trade Management (1:1, 1:2, 1:3).
        Magic: 10501
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        management_orders = []

        for trade in active_trades:
            ticket = trade['ticket']
            entry = trade['entry_price']
            sl = trade['sl_price']
            action = trade['action']

            # Use original SL pts to determine Risk unit (1R)
            sl_pts = trade.get('sl_pts', 0)
            if sl_pts == 0: continue

            # Fetch tick size for price calculation
            s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
            ts = s_stats.get("tick_size", 0.0001)
            r_dist = sl_pts * ts

            # 1:1 Risk-to-Reward Progression
            # Move SL to Breakeven at 1:1 RR
            one_r_level = entry + r_dist if action == "BUY" else entry - r_dist
            is_one_r_hit = (action == "BUY" and current_price >= one_r_level) or (action == "SELL" and current_price <= one_r_level)

            # 1:2 Risk-to-Reward Progression
            # Move SL to 1:1 RR (1R Profit) at 1:2 RR
            two_r_level = entry + 2 * r_dist if action == "BUY" else entry - 2 * r_dist
            is_two_r_hit = (action == "BUY" and current_price >= two_r_level) or (action == "SELL" and current_price <= two_r_level)

            # 1:3 Risk-to-Reward Progression
            # Move SL to 1:2 RR (2R Profit) at 1:3 RR
            three_r_level = entry + 3 * r_dist if action == "BUY" else entry - 3 * r_dist
            is_three_r_hit = (action == "BUY" and current_price >= three_r_level) or (action == "SELL" and current_price <= three_r_level)

            target_sl = sl

            if is_three_r_hit:
                # Lock in 2R profit
                target_sl = entry + 2 * r_dist if action == "BUY" else entry - 2 * r_dist
            elif is_two_r_hit:
                # Lock in 1R profit
                target_sl = entry + r_dist if action == "BUY" else entry - r_dist
            elif is_one_r_hit:
                # Move to Breakeven
                target_sl = entry

            # Only update if SL is moving in our favor
            should_update = False
            if action == "BUY" and target_sl > sl: should_update = True
            elif action == "SELL" and target_sl < sl: should_update = True

            if should_update:
                management_orders.append({
                    "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": ticket,
                    "s": symbol, "sl": target_sl, "reason": "RR_MANAGEMENT_PROGRESSED"
                })

        return management_orders
