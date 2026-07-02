import logging
import time
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """10500: Institutional Position Lifecycle Management (V3.3.0-ASCENDANT)."""
    def __init__(self, ledger: TradeLedger, risk_manager: RiskManager):
        self.ledger = ledger
        self.risk_manager = risk_manager

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float, smc_data: Optional[Dict[str, Any]] = None, mtf_trends: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """10505: Master management entry point with Scaling logic."""
        current_price = (bid + ask) / 2

        # 1. Trailing and Shared SL Management
        orders = await self.manage_open_positions(symbol, current_price, atr, smc_data)

        # 2. Scaling Logic: Add 0.01 lots if trade is in profit and trend is in favor
        active_trades = await self.ledger.get_active_trades_db(symbol)
        if active_trades and mtf_trends:
            # Rule 1.b: "only if all the previous trades are running in profit"
            all_in_profit = True
            for t in active_trades:
                profit = (current_price - t["entry_price"]) if t["action"] == "BUY" else (t["entry_price"] - current_price)
                if profit <= 0:
                    all_in_profit = False
                    break

            if all_in_profit:
                # Use the most recent trade to check if profit is "locked" (SL at or better than Entry)
                # This ensures we scale in a 1:1, 1:2, 1:3 RR progression pattern
                last_trade = sorted(active_trades, key=lambda x: x['timestamp'])[-1]
                is_locked = False
                if last_trade["action"] == "BUY" and last_trade["sl_price"] >= last_trade["entry_price"]: is_locked = True
                if last_trade["action"] == "SELL" and last_trade["sl_price"] <= last_trade["entry_price"]: is_locked = True

                if is_locked:
                    trend = "BULLISH" if last_trade["action"] == "BUY" else "BEARISH"
                    # Rule 2.a/b: Mandatory Higher TF Assessment (M15, H1, H4, D1)
                    # For scaling, we check H1 and H4 alignment as a proxy for "Higher TF"
                    if mtf_trends.get("h1") == trend and mtf_trends.get("h4") == trend:
                        orders.append({
                            "type": "PROBABILISTIC_SIGNAL",
                            "symbol": symbol,
                            "action": last_trade["action"],
                            "probability": 0.90,
                            "reason": "SCALING_IN_PROGRESSION",
                            "atr": atr,
                            "scaling": True
                        })

        return orders

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float, smc_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        10501: Shared Trailing SL Management.
        Rule: All trades for same symbol/direction MUST share the same SL.
        """
        active_trades = await self.ledger.get_active_trades_db(symbol)
        if not active_trades: return []

        # Group by direction
        buys = [t for t in active_trades if t['action'] == 'BUY']
        sells = [t for t in active_trades if t['action'] == 'SELL']

        management_orders = []

        for trades in [buys, sells]:
            if not trades: continue

            direction = trades[0]['action']
            s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
            ts = s_stats.get("tick_size", 0.0001)

            # Find the "Leading" SL based on RR progression of EACH trade
            # But the rule says SL must be same for ALL.
            # We will calculate the trailing SL for each and take the most aggressive one.

            best_sl = 0.0
            current_sl = trades[0]['sl_price'] # They should ideally be same already

            for trade in trades:
                entry = trade['entry_price']
                sl_pts = trade.get('sl_pts', 0)
                if sl_pts == 0: continue

                r_dist = sl_pts * ts

                # RR Levels
                one_r = entry + r_dist if direction == "BUY" else entry - r_dist
                two_r = entry + 2 * r_dist if direction == "BUY" else entry - 2 * r_dist
                three_r = entry + 3 * r_dist if direction == "BUY" else entry - 3 * r_dist

                # Proposed SL for THIS trade
                p_sl = trade['sl_price']
                if direction == "BUY":
                    if current_price >= three_r: p_sl = entry + 2 * r_dist
                    elif current_price >= two_r: p_sl = entry + r_dist
                    elif current_price >= one_r: p_sl = entry

                    if best_sl == 0 or p_sl > best_sl: best_sl = p_sl
                else:
                    if current_price <= three_r: p_sl = entry - 2 * r_dist
                    elif current_price <= two_r: p_sl = entry - r_dist
                    elif current_price <= one_r: p_sl = entry

                    if best_sl == 0 or p_sl < best_sl: best_sl = p_sl

            # If best_sl moved, apply to ALL trades in this direction
            if best_sl > 0:
                for trade in trades:
                    # Update if SL improved
                    if (direction == "BUY" and best_sl > trade['sl_price']) or                        (direction == "SELL" and best_sl < trade['sl_price']):
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": trade['ticket'],
                            "s": symbol, "sl": best_sl, "reason": "SHARED_TRAILING_RR"
                        })

        return management_orders
