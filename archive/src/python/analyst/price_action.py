import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class SMCAnalyst:
    """12006: Smart Money Concepts pattern recognition."""
    def detect_market_structure(self, df: pd.DataFrame, atr: float = 0.0) -> Dict[str, Any]:
        """
        Analyze market structure by identifying pivot points, trend direction, and reversal signals.
        """
        if len(df) < 15: return {"trend": "NEUTRAL", "choch": False, "sweep": False, "swing_h": None, "swing_l": None}
        h = df['h'].values; l = df['l'].values; c = df['c'].values
        pivot_h_mask = (h[2:-2] > h[0:-4]) & (h[2:-2] > h[1:-3]) & (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
        pivot_l_mask = (l[2:-2] < l[0:-4]) & (l[2:-2] < l[1:-3]) & (l[2:-2] < l[3:-1]) & (l[2:-2] < l[4:])
        pivot_h_idx = np.where(pivot_h_mask)[0] + 2
        pivot_l_idx = np.where(pivot_l_mask)[0] + 2
        highs = h[pivot_h_idx][-3:]; lows = l[pivot_l_idx][-3:]
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
        return {"trend": trend, "choch": choch, "sweep": sweep, "swing_h": highs[-1] if len(highs) > 0 else None, "swing_l": lows[-1] if len(lows) > 0 else None}

    def detect_order_blocks(self, df: pd.DataFrame, atr: float = 0.0) -> List[Dict[str, Any]]:
        """
        Identify bullish and bearish order blocks based on impulsive candle reversals.
        """
        if len(df) < 5: return []
        o = df['o'].values; h = df['h'].values; l = df['l'].values; c = df['c'].values
        move_sizes = np.abs(c[1:] - o[1:]); atr_threshold = atr * 1.5 if atr > 0 else 0
        impulsive_mask = move_sizes > atr_threshold
        bullish_ob_mask = (c[:-1] < o[:-1]) & (c[1:] > o[1:]) & impulsive_mask
        bearish_ob_mask = (c[:-1] > o[:-1]) & (c[1:] < o[1:]) & impulsive_mask
        obs = []
        for idx in np.where(bullish_ob_mask)[0]: obs.append({"type": "BULLISH", "top": h[idx], "bottom": l[idx], "index": int(idx)})
        for idx in np.where(bearish_ob_mask)[0]: obs.append({"type": "BEARISH", "top": h[idx], "bottom": l[idx], "index": int(idx)})
        return obs[-5:]

    def detect_fvg(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        12015: Detect Fair Value Gaps (FVG).
        A FVG occurs when there is a gap between the low of candle 1 and the high of candle 3 in an impulsive move.
        """
        if len(df) < 3: return []
        h = df['h'].values; l = df['l'].values
        fvgs = []
        for i in range(2, len(df)):
            if h[i-2] < l[i]: # Bullish FVG
                fvgs.append({"type": "BULLISH", "top": l[i], "bottom": h[i-2], "index": i-1})
            elif l[i-2] > h[i]: # Bearish FVG
                fvgs.append({"type": "BEARISH", "top": l[i-2], "bottom": h[i], "index": i-1})
        return fvgs[-5:]

    def detect_inducement(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        12016: Detect Inducement (IDM).
        IDM is the first pullback in a new trend that retail traders often mistake for a reversal.
        """
        struct = self.detect_market_structure(df)
        if struct["trend"] == "NEUTRAL": return None
        l = df['l'].values; h = df['h'].values
        if struct["trend"] == "BULLISH":
            # Inducement is the last valid low before a new high
            if len(l) > 5: return {"type": "IDM_BULLISH", "level": np.min(l[-5:-1])}
        elif struct["trend"] == "BEARISH":
            # Inducement is the last valid high before a new low
            if len(h) > 5: return {"type": "IDM_BEARISH", "level": np.max(h[-5:-1])}
        return None

    def detect_candlestick_trigger(self, df: pd.DataFrame) -> str:
        """
        Classifies the latest candlestick into a price-action trigger pattern.
        """
        if len(df) < 2: return None
        last = df.iloc[-1]; prev = df.iloc[-2]
        body = abs(last['c'] - last['o']); r_size = last['h'] - last['l']
        if r_size > body * 3:
            if last['c'] > last['o'] and (last['h'] - last['c']) < (last['o'] - last['l']): return "BULLISH_PIN"
            if last['c'] < last['o'] and (last['c'] - last['l']) < (last['h'] - last['o']): return "BEARISH_PIN"
        if last['c'] > prev['h'] and last['o'] < prev['l'] and last['c'] > last['o']: return "BULLISH_ENGULFING"
        if last['c'] < prev['l'] and last['o'] > prev['h'] and last['c'] < last['o']: return "BEARISH_ENGULFING"
        return None
