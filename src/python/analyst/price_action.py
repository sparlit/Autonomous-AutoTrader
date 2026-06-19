import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class SMCAnalyst:
    def __init__(self):
        pass

    def detect_market_structure(self, df: pd.DataFrame, atr: float = 0.0) -> Dict[str, Any]:
        """Detect Higher Highs, Lower Lows, and CHoCH with Sweep awareness."""
        if len(df) < 15:
            return {"trend": "NEUTRAL", "choch": False, "sweep": False}

        # Robust pivot detection
        df['pivot_h'] = (df['h'] > df['h'].shift(1)) & (df['h'] > df['h'].shift(2)) &                         (df['h'] > df['h'].shift(-1)) & (df['h'] > df['h'].shift(-2))
        df['pivot_l'] = (df['l'] < df['l'].shift(1)) & (df['l'] < df['l'].shift(2)) &                         (df['l'] < df['l'].shift(-1)) & (df['l'] < df['l'].shift(-2))

        highs = df[df['pivot_h']]['h'].tail(3).values
        lows = df[df['pivot_l']]['l'].tail(3).values

        # Liquidity Sweep Detection: Price pierced the last major pivot but closed back inside
        sweep = False
        if len(highs) >= 2:
            last_major_h = highs[-2]
            if df['h'].iloc[-1] > last_major_h and df['c'].iloc[-1] < last_major_h:
                sweep = "BEARISH_SWEEP" # Bullish fakeout
        if not sweep and len(lows) >= 2:
            last_major_l = lows[-2]
            if df['l'].iloc[-1] < last_major_l and df['c'].iloc[-1] > last_major_l:
                sweep = "BULLISH_SWEEP" # Bearish fakeout

        trend = "NEUTRAL"
        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                trend = "BULLISH"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                trend = "BEARISH"

        choch = False
        if trend == "BULLISH" and df['c'].iloc[-1] < lows[-1]:
            choch = True
        elif trend == "BEARISH" and df['c'].iloc[-1] > highs[-1]:
            choch = True

        return {"trend": trend, "choch": choch, "sweep": sweep}

    def detect_order_blocks(self, df: pd.DataFrame, atr: float = 0.0) -> List[Dict[str, Any]]:
        obs = []
        atr_threshold = atr * 1.5 if atr > 0 else 0
        for i in range(5, len(df) - 1):
            move_size = abs(df['c'].iloc[i] - df['o'].iloc[i])
            if move_size > atr_threshold:
                if df['c'].iloc[i] > df['o'].iloc[i] and df['c'].iloc[i-1] < df['o'].iloc[i-1]:
                    obs.append({"type": "BULLISH", "top": df['h'].iloc[i-1], "bottom": df['l'].iloc[i-1], "index": i-1})
                elif df['c'].iloc[i] < df['o'].iloc[i] and df['c'].iloc[i-1] > df['o'].iloc[i-1]:
                    obs.append({"type": "BEARISH", "top": df['h'].iloc[i-1], "bottom": df['l'].iloc[i-1], "index": i-1})
        return obs[-5:]
