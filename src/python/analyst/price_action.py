import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class SMCAnalyst:
    def __init__(self):
        pass

    def detect_market_structure(self, df: pd.DataFrame, atr: float = 0.0) -> Dict[str, Any]:
        """Detect Market Structure using vectorized pivot logic."""
        if len(df) < 15:
            return {"trend": "NEUTRAL", "choch": False, "sweep": False, "swing_h": None, "swing_l": None}

        # Vectorized Pivot Detection (5-bar window)
        h = df['h'].values; l = df['l'].values; c = df['c'].values

        pivot_h_mask = (h[2:-2] > h[0:-4]) & (h[2:-2] > h[1:-3]) &                        (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
        pivot_l_mask = (l[2:-2] < l[0:-4]) & (l[2:-2] < l[1:-3]) &                        (l[2:-2] < l[3:-1]) & (l[2:-2] < l[4:])

        # Pad masks to match original length
        pivot_h_idx = np.where(pivot_h_mask)[0] + 2
        pivot_l_idx = np.where(pivot_l_mask)[0] + 2

        highs = h[pivot_h_idx][-3:]
        lows = l[pivot_l_idx][-3:]

        # Sweep Detection (Vectorized)
        sweep = False
        if len(highs) >= 2:
            if h[-1] > highs[-2] and c[-1] < highs[-2]: sweep = "BEARISH_SWEEP"
        if not sweep and len(lows) >= 2:
            if l[-1] < lows[-2] and c[-1] > lows[-2]: sweep = "BULLISH_SWEEP"

        trend = "NEUTRAL"
        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]: trend = "BULLISH"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]: trend = "BEARISH"

        choch = False
        if trend == "BULLISH" and c[-1] < lows[-1]: choch = True
        elif trend == "BEARISH" and c[-1] > highs[-1]: choch = True

        return {
            "trend": trend, "choch": choch, "sweep": sweep,
            "swing_h": highs[-1] if len(highs) > 0 else None,
            "swing_l": lows[-1] if len(lows) > 0 else None
        }

    def detect_order_blocks(self, df: pd.DataFrame, atr: float = 0.0) -> List[Dict[str, Any]]:
        """Optimized OB detection using vectorized conditions."""
        if len(df) < 5: return []
        o = df['o'].values; h = df['h'].values; l = df['l'].values; c = df['c'].values

        move_sizes = np.abs(c[1:] - o[1:])
        atr_threshold = atr * 1.5 if atr > 0 else 0

        impulsive_mask = move_sizes > atr_threshold
        # Bullish OB: Red candle (c < o) followed by impulsive Green candle (c > o)
        bullish_ob_mask = (c[:-1] < o[:-1]) & (c[1:] > o[1:]) & impulsive_mask
        # Bearish OB: Green candle followed by impulsive Red candle
        bearish_ob_mask = (c[:-1] > o[:-1]) & (c[1:] < o[1:]) & impulsive_mask

        obs = []
        for idx in np.where(bullish_ob_mask)[0]:
            obs.append({"type": "BULLISH", "top": h[idx], "bottom": l[idx], "index": int(idx)})
        for idx in np.where(bearish_ob_mask)[0]:
            obs.append({"type": "BEARISH", "top": h[idx], "bottom": l[idx], "index": int(idx)})

        return obs[-5:]

    def detect_candlestick_trigger(self, df: pd.DataFrame) -> str:
        if len(df) < 2: return None
        last = df.iloc[-1]; prev = df.iloc[-2]
        body = abs(last['c'] - last['o'])
        range_size = last['h'] - last['l']
        if range_size > body * 3:
            if last['c'] > last['o'] and (last['h'] - last['c']) < (last['o'] - last['l']): return "BULLISH_PIN"
            if last['c'] < last['o'] and (last['c'] - last['l']) < (last['h'] - last['o']): return "BEARISH_PIN"
        if last['c'] > prev['h'] and last['o'] < prev['l'] and last['c'] > last['o']: return "BULLISH_ENGULFING"
        if last['c'] < prev['l'] and last['o'] > prev['h'] and last['c'] < last['o']: return "BEARISH_ENGULFING"
        return None
