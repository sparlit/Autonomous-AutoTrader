import logging
import time
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """V4.0: Institutional Position Lifecycle & vRR Management."""
    def __init__(self, ledger: TradeLedger, risk_manager: RiskManager):
        self.ledger = ledger
        self.risk_manager = risk_manager
        self.inst = risk_manager.config.institutional

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float, mtf_trends: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """V4.0: Master management entry point."""
        if bid <= 0 or ask <= 0: return []
        current_price = (bid + ask) / 2

        # 1. Manage existing positions (Profit Locking, TTP, Shared SL)
        orders = await self.manage_open_positions(symbol, current_price, atr)

        # 2. Scaling Logic (Rule 1.c)
        all_trades = await self.ledger.get_all_active_trades()
        sym_trades = [t for t in all_trades if t['symbol'] == symbol and t['status'] == 'OPEN']

        if sym_trades and mtf_trends:
            can_scale = True
            total_profit = 0.0

            s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
            tick_val = float(s_stats.get("tick_val") or 10.0)
            tick_size = float(s_stats.get("tick_size") or 0.0001)

            for t in sym_trades:
                entry = float(t['entry_price'])
                diff = (current_price - entry) if t['action'] == "BUY" else (entry - current_price)

                pips = diff / tick_size if tick_size > 0 else 0
                trade_profit = t['lots'] * pips * tick_val
                total_profit += trade_profit

                # Rule 1.c.ii: if existing trade is in loss or profit < 1 USD, no trade
                if trade_profit < self.inst.min_profit_scaling_usd:
                    can_scale = False
                    break

            if can_scale and total_profit >= self.inst.min_profit_scaling_usd:
                direction = sym_trades[0]['action']
                trend = mtf_trends.get("h1", "NEUTRAL")
                if (direction == "BUY" and trend == "BULLISH") or (direction == "SELL" and trend == "BEARISH"):
                    # Check if profit is "locked" (SL at BE or better)
                    if all(float(t.get('sl_price', 0)) >= float(t['entry_price']) if t['action'] == "BUY" else (float(t.get('sl_price', 0)) > 0 and float(t.get('sl_price', 0)) <= float(t['entry_price'])) for t in sym_trades):
                         orders.append({
                            "type": "PROBABILISTIC_SIGNAL",
                            "symbol": symbol,
                            "action": direction,
                            "probability": 0.95,
                            "reason": "SCALING_QUALIFIED",
                            "atr": atr,
                            "scaling": True
                        })

        return orders

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
        """V4.0: Profit Locking, Trailing SL, and TTP."""
        all_trades = await self.ledger.get_all_active_trades()
        active_trades = [t for t in all_trades if t['symbol'] == symbol and t['status'] == 'OPEN']
        if not active_trades: return []

        management_orders = []
        s_stats = self.risk_manager.ipc.get_state(f"symbol_stats:{symbol}", {})
        ts = float(s_stats.get("tick_size") or 0.0001)
        tv = float(s_stats.get("tick_val") or 10.0)

        for trade in active_trades:
            entry = float(trade['entry_price'])
            action = trade['action']
            sl_price = float(trade.get('sl_price') or 0.0)
            tp_price = float(trade.get('tp_price') or 0.0)
            ticket = int(trade['ticket'])

            diff = (current_price - entry) if action == "BUY" else (entry - current_price)
            pips = diff / ts if ts > 0 else 0
            profit_usd = trade['lots'] * pips * tv

            # Rule: Never Close in Loss (Lock Profit at BE+)
            if profit_usd >= 1.0:
                # Lock BE + -bash.10 buffer
                offset = (0.10 / (trade['lots'] * tv)) * ts if trade['lots'] > 0 else 0
                be_price = entry + offset if action == "BUY" else entry - offset

                if (action == "BUY" and sl_price < be_price) or (action == "SELL" and (sl_price == 0 or sl_price > be_price)):
                     management_orders.append({
                        "type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": ticket,
                        "s": symbol, "sl": float(be_price), "reason": "PROFIT_LOCKED_V4"
                    })

            # Trailing Take Profit (TTP) Logic
            tp_dist = abs(tp_price - entry)
            if tp_dist > 0:
                progress = diff / tp_dist
                if progress >= 0.9:
                    # Move TP further and activate trailing stop with tight 0.5 ATR buffer
                    new_tp = current_price + (atr * 2) if action == "BUY" else current_price - (atr * 2)
                    new_sl = current_price - (atr * 0.5) if action == "BUY" else current_price + (atr * 0.5)

                    if (action == "BUY" and new_sl > sl_price) or (action == "SELL" and (sl_price == 0 or new_sl < sl_price)):
                        management_orders.append({
                            "type": "EXECUTION_ORDER", "t": "MODIFY_ALL", "tk": ticket,
                            "s": symbol, "sl": float(new_sl), "tp": float(new_tp), "reason": "TTP_ACTIVATED"
                        })

        return management_orders
