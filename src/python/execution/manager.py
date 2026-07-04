import logging
import time
from typing import Dict, Any, List, Optional
from src.python.execution.ledger import TradeLedger
from src.python.execution.risk_manager import RiskManager

logger = logging.getLogger("AAT_PositionManager")

class PositionManager:
    """V4.0: Institutional Position Lifecycle & Retroactive SL/TP Management."""
    def __init__(self, ledger: TradeLedger, risk_manager: RiskManager):
        self.ledger = ledger
        self.risk_manager = risk_manager
        self.inst = risk_manager.config.institutional

    async def monitor_and_manage(self, symbol: str, bid: float, ask: float, atr: float, mtf_trends: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if bid <= 0 or ask <= 0: return []
        current_price = (bid + ask) / 2
        orders = await self.manage_open_positions(symbol, current_price, atr)

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
                if trade_profit < self.inst.min_profit_scaling_usd:
                    can_scale = False
                    break

            if can_scale and total_profit >= self.inst.min_profit_scaling_usd:
                direction = sym_trades[0]['action']
                trend = mtf_trends.get("h1", "NEUTRAL")
                if (direction == "BUY" and trend == "BULLISH") or (direction == "SELL" and trend == "BEARISH"):
                    if all(float(t.get('sl_price', 0)) >= float(t['entry_price']) if t['action'] == "BUY" else (float(t.get('sl_price', 0)) > 0 and float(t.get('sl_price', 0)) <= float(t['entry_price'])) for t in sym_trades):
                         orders.append({"type": "PROBABILISTIC_SIGNAL", "symbol": symbol, "action": direction, "probability": 0.95, "reason": "SCALING_QUALIFIED", "atr": atr, "scaling": True})
        return orders

    async def manage_open_positions(self, symbol: str, current_price: float, atr: float) -> List[Dict[str, Any]]:
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
            sl_p = float(trade.get('sl_price') or 0.0)
            tp_p = float(trade.get('tp_price') or 0.0)
            ticket = int(trade['ticket'])

            # 1. Retroactive SL/TP Calculation (Rule 1.b.viii fallback)
            if sl_p == 0 or tp_p == 0:
                if atr > 0:
                    sl_dist = atr * 2
                    tp_dist = sl_dist * 2 # Default 1:2 for legacy fixes

                    new_sl = entry - sl_dist if action == "BUY" else entry + sl_dist
                    new_tp = entry + tp_dist if action == "BUY" else entry - tp_dist

                    management_orders.append({
                        "type": "EXECUTION_ORDER", "t": "MODIFY_ALL", "tk": ticket,
                        "s": symbol, "sl": float(new_sl), "tp": float(new_tp), "reason": "RETROACTIVE_STOPS_SET"
                    })
                    # Update local ref for following logic
                    sl_p = new_sl; tp_p = new_tp

            diff = (current_price - entry) if action == "BUY" else (entry - current_price)
            pips = diff / ts if ts > 0 else 0
            profit_usd = trade['lots'] * pips * tv

            # 2. Profit Locking (BE+)
            if profit_usd >= 1.0:
                offset = (0.10 / (trade['lots'] * tv)) * ts if trade['lots'] > 0 else 0
                be_price = entry + offset if action == "BUY" else entry - offset
                if (action == "BUY" and sl_p < be_price) or (action == "SELL" and (sl_p == 0 or sl_p > be_price)):
                     management_orders.append({"type": "EXECUTION_ORDER", "t": "MODIFY_SL", "tk": ticket, "s": symbol, "sl": float(be_price), "reason": "PROFIT_LOCKED_V4"})

            # 3. Trailing Take Profit (TTP)
            tp_dist = abs(tp_p - entry)
            if tp_dist > 0:
                progress = diff / tp_dist
                if progress >= 0.9:
                    new_tp = current_price + (atr * 2) if action == "BUY" else current_price - (atr * 2)
                    new_sl = current_price - (atr * 0.5) if action == "BUY" else current_price + (atr * 0.5)
                    if (action == "BUY" and new_sl > sl_p) or (action == "SELL" and (sl_p == 0 or new_sl < sl_p)):
                        management_orders.append({"type": "EXECUTION_ORDER", "t": "MODIFY_ALL", "tk": ticket, "s": symbol, "sl": float(new_sl), "tp": float(new_tp), "reason": "TTP_ACTIVATED"})

        return management_orders
