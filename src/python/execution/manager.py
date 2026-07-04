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
        """10505: Master management entry point with Scaling logic (V3.3.3 Rules)."""
        if bid <= 0 or ask <= 0: return []

        current_price = (bid + ask) / 2

        # 1. Trailing and Shared SL Management (Rule 1.d)
        orders = await self.manage_open_positions(symbol, current_price, atr, smc_data)

        # 2. Scaling Logic: Add 0.01 lots if trade is in profit and trend is in favor (Rule 1.c)
        all_trades = await self.ledger.get_all_active_trades()
        sym_trades = [t for t in all_trades if t['symbol'] == symbol]

        # Rule 1.c: Block if there are ANY pending trades for this symbol
        if any(t['status'] == 'PENDING' for t in sym_trades):
            return orders

        active_trades = [t for t in sym_trades if t['status'] == 'OPEN']

        if active_trades and mtf_trends:
            # Rule 1.c.ii: if the existing trade is in loss or profit less than 1 USD, no trade
            all_qualified = True
            s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
            tick_val = float(s_stats.get("tick_val") or 10.0)
            tick_size = float(s_stats.get("tick_size") or 0.0001)

            for t in active_trades:
                entry = float(t.get("entry_price") or 0.0)
                if entry == 0:
                    all_qualified = False; break

                diff = (current_price - entry) if t["action"] == "BUY" else (entry - current_price)
                pips = diff / tick_size if tick_size > 0 else 0
                profit_usd = t["lots"] * pips * tick_val if tick_size > 0 else 0

                if profit_usd < 1.0: # Rule 1.c.ii
                    all_qualified = False; break

            if all_qualified:
                # Rule 1.c: Acquire Trading Lock for Scaling (Zero-Tolerance)
                if not self.risk_manager.ipc.acquire_trading_lock(symbol, cooldown=60):
                    return orders

                # Use the most recent trade to check if profit is "locked" (SL at or better than Entry)
                last_trade = sorted(active_trades, key=lambda x: x['timestamp'])[-1]
                is_locked = False
                sl_p = float(last_trade.get("sl_price") or 0.0)
                en_p = float(last_trade.get("entry_price") or 0.0)

                if last_trade["action"] == "BUY" and sl_p >= en_p: is_locked = True
                if last_trade["action"] == "SELL" and sl_p <= en_p: is_locked = True

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
        10501: Shared Trailing SL Management (Rule 1.c.xiii / 1.d).
        Rule: All trades for same symbol/direction MUST share the same SL.
        """
        all_trades = await self.ledger.get_all_active_trades()
        active_trades = [t for t in all_trades if t['symbol'] == symbol and t['status'] == 'OPEN']
        if not active_trades: return []

        # Group by direction
        buys = [t for t in active_trades if t['action'] == 'BUY']
        sells = [t for t in active_trades if t['action'] == 'SELL']

        management_orders = []

        for trades in [buys, sells]:
            if not trades: continue

            direction = trades[0]['action']
            s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
            ts = float(s_stats.get("tick_size") or 0.0001)

            best_sl = 0.0

            for trade in trades:
                entry = float(trade['entry_price'])
                sl_price = float(trade.get('sl_price') or 0.0)
                sl_pts = trade.get('sl_pts', 0)

                if not sl_pts or sl_pts == 0:
                    sl_pts = int(abs(entry - sl_price) / ts) if ts > 0 and sl_price > 0 else 100

                r_dist = sl_pts * ts
                if r_dist <= 0: continue

                # RR Levels
                one_r = entry + r_dist if direction == "BUY" else entry - r_dist
                two_r = entry + 2 * r_dist if direction == "BUY" else entry - 2 * r_dist
                three_r = entry + 3 * r_dist if direction == "BUY" else entry - 3 * r_dist

                p_sl = sl_price
                if direction == "BUY":
                    if current_price >= three_r: p_sl = entry + 2 * r_dist  # 1:3 RR -> Lock 2R
                    elif current_price >= two_r: p_sl = entry + r_dist     # 1:2 RR -> Lock 1R
                    elif current_price >= one_r: p_sl = entry              # 1:1 RR -> Lock BE

                    if best_sl == 0 or p_sl > best_sl: best_sl = p_sl
                else:
                    if current_price <= three_r: p_sl = entry - 2 * r_dist # 1:3 RR -> Lock 2R
                    elif current_price <= two_r: p_sl = entry - r_dist     # 1:2 RR -> Lock 1R
                    elif current_price <= one_r: p_sl = entry              # 1:1 RR -> Lock BE

                    if best_sl == 0 or (p_sl > 0 and p_sl < best_sl): best_sl = p_sl

            if best_sl > 0:
                for trade in trades:
                    current_sl = float(trade.get('sl_price') or 0.0)
                    if (direction == "BUY" and best_sl > current_sl) or                        (direction == "SELL" and (current_sl == 0 or best_sl < current_sl)):
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": int(trade['ticket']),
                            "s": symbol, "sl": float(best_sl), "reason": "SHARED_TRAILING_RR"
                        })

        return management_orders
