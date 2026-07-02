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
                last_trade = sorted(active_trades, key=lambda x: x['timestamp'])[-1]
                is_locked = False
                if last_trade["action"] == "BUY" and last_trade["sl_price"] >= last_trade["entry_price"]: is_locked = True
                if last_trade["action"] == "SELL" and last_trade["sl_price"] <= last_trade["entry_price"]: is_locked = True

                if is_locked:
                    # PROPOSE SCALING - HiveOrchestrator and RiskBrain will mandate Trend Confirmation
                    orders.append({
                        "type": "PROBABILISTIC_SIGNAL",
                        "symbol": symbol,
                        "action": last_trade["action"],
                        "probability": 0.95,
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
        active_trades = await self.ledger.get_all_active_trades()
        active_trades = [t for t in active_trades if t['symbol'] == symbol]
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

            best_sl = 0.0

            for trade in trades:
                entry = trade['entry_price']
                sl_pts = trade.get('sl_pts', 0)
                if not sl_pts or sl_pts == 0:
                    sl_pts = int(abs(entry - trade['sl_price']) / ts) if ts > 0 else 100

                r_dist = sl_pts * ts
                if r_dist <= 0: continue

                # RR Levels
                one_r = entry + r_dist if direction == "BUY" else entry - r_dist
                two_r = entry + 2 * r_dist if direction == "BUY" else entry - 2 * r_dist
                three_r = entry + 3 * r_dist if direction == "BUY" else entry - 3 * r_dist

                p_sl = trade['sl_price']
                if direction == "BUY":
                    if current_price >= three_r: p_sl = entry + 2 * r_dist  # 1:3 RR -> Lock 2R
                    elif current_price >= two_r: p_sl = entry + r_dist     # 1:2 RR -> Lock 1R
                    elif current_price >= one_r: p_sl = entry              # 1:1 RR -> Lock BE

                    if best_sl == 0 or p_sl > best_sl: best_sl = p_sl
                else:
                    if current_price <= three_r: p_sl = entry - 2 * r_dist # 1:3 RR -> Lock 2R
                    elif current_price <= two_r: p_sl = entry - r_dist     # 1:2 RR -> Lock 1R
                    elif current_price <= one_r: p_sl = entry              # 1:1 RR -> Lock BE

                    if best_sl == 0 or p_sl < best_sl: best_sl = p_sl

            if best_sl > 0:
                for trade in trades:
                    if (direction == "BUY" and best_sl > trade['sl_price']) or                        (direction == "SELL" and best_sl < trade['sl_price']):
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": trade['ticket'],
                            "s": symbol, "sl": best_sl, "reason": "SHARED_TRAILING_RR"
                        })

        return management_orders
