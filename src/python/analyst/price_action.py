import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class SMCAnalyst:
    def __init__(self):
        pass

    def detect_market_structure(self, df: pd.DataFrame, atr: float = 0.0) -> Dict[str, Any]:
        """Detect Higher Highs, Lower Lows, and CHoCH with Pivot confirmation."""
        if len(df) < 15:
            return {"trend": "NEUTRAL", "choch": False}

        # Robust pivot detection (3-bar confirmation)
        df['pivot_h'] = (df['h'] > df['h'].shift(1)) & (df['h'] > df['h'].shift(2)) &                         (df['h'] > df['h'].shift(-1)) & (df['h'] > df['h'].shift(-2))
        df['pivot_l'] = (df['l'] < df['l'].shift(1)) & (df['l'] < df['l'].shift(2)) &                         (df['l'] < df['l'].shift(-1)) & (df['l'] < df['l'].shift(-2))

        highs = df[df['pivot_h']]['h'].tail(3).values
        lows = df[df['pivot_l']]['l'].tail(3).values

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

        return {"trend": trend, "choch": choch}

    def detect_order_blocks(self, df: pd.DataFrame, atr: float = 0.0) -> List[Dict[str, Any]]:
        """Identify Order Blocks using ATR-relative impulsive move detection."""
        obs = []
        atr_threshold = atr * 1.5 if atr > 0 else 0

        for i in range(5, len(df) - 1):
            move_size = abs(df['c'].iloc[i] - df['o'].iloc[i])

            # Impulsive move must be > 1.5x ATR to be an institutional OB
            if move_size > atr_threshold:
                # Bullish OB: Impulsive green candle after a red candle
                if df['c'].iloc[i] > df['o'].iloc[i] and df['c'].iloc[i-1] < df['o'].iloc[i-1]:
                    obs.append({
                        "type": "BULLISH",
                        "top": df['h'].iloc[i-1],
                        "bottom": df['l'].iloc[i-1],
                        "index": i-1
                    })
                # Bearish OB: Impulsive red candle after a green candle
                elif df['c'].iloc[i] < df['o'].iloc[i] and df['c'].iloc[i-1] > df['o'].iloc[i-1]:
                    obs.append({
                        "type": "BEARISH",
                        "top": df['h'].iloc[i-1],
                        "bottom": df['l'].iloc[i-1],
                        "index": i-1
                    })
        return obs[-5:]

    def detect_fvg(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        fvgs = []
        for i in range(1, len(df) - 1):
            if df['l'].iloc[i+1] > df['h'].iloc[i-1]:
                fvgs.append({"type": "BULLISH", "top": df['l'].iloc[i+1], "bottom": df['h'].iloc[i-1]})
            if df['h'].iloc[i+1] < df['l'].iloc[i-1]:
                fvgs.append({"type": "BEARISH", "top": df['l'].iloc[i-1], "bottom": df['h'].iloc[i+1]})
        return fvgs[-5:]
