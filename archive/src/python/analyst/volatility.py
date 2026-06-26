import pandas as pd
import numpy as np
from typing import Dict, Any

class VolatilityAnalyst:
    """12007: Volume-Spread and market regime analysis."""
    def is_spread_safe(self, current_spread: float, avg_spread: float, threshold_multiplier: float = 2.0) -> bool:
        """12008: Spread safety check."""
        return current_spread <= (avg_spread * threshold_multiplier)

    def get_regime(self, df: pd.DataFrame) -> str:
        """
        12009: Enhanced Multi-regime classification.
        Classifies market into: TRENDING_FAST, TRENDING_SLOW, RANGING_WIDE, RANGING_TIGHT, HIGH_VOLATILITY, CRASH_SUDDEN.
        """
        if len(df) < 30: return "NORMAL"

        c = df['c']
        h = df['h']
        l = df['l']

        atr = (h - l).rolling(20).mean()
        curr_atr = atr.iloc[-1]
        avg_atr = atr.mean()

        # Trendiness via Linear Regression slope or simple distance
        price_delta = c.iloc[-1] - c.iloc[-20]
        abs_delta = abs(price_delta)
        vol_adjusted_move = abs_delta / (curr_atr * np.sqrt(20))

        # Volume spikes
        avg_vol = df['v'].rolling(20).mean().iloc[-1]
        curr_vol = df['v'].iloc[-1]

        if abs_delta > curr_atr * 5 and curr_vol > avg_vol * 3:
            return "CRASH_SUDDEN" if price_delta < 0 else "SPIKE_SUDDEN"

        if curr_atr > avg_atr * 2.0:
            return "HIGH_VOLATILITY"

        if vol_adjusted_move > 2.0:
            return "TRENDING_FAST"
        elif vol_adjusted_move > 1.0:
            return "TRENDING_SLOW"

        if curr_atr < avg_atr * 0.6:
            return "RANGING_TIGHT"

        return "NORMAL"

    def analyze_vsa(self, df: pd.DataFrame) -> Dict[str, Any]:
        """12011: Advanced Volume-Spread Analysis."""
        if len(df) < 20: return {"effort": "NEUTRAL", "result": "NEUTRAL", "anomaly": False, "volume_ratio": 1.0}
        avg_v = df['v'].rolling(20).mean().iloc[-1]
        last_v = df['v'].iloc[-1]
        spread = abs(df['c'].iloc[-1] - df['o'].iloc[-1])
        avg_s = abs(df['c'] - df['o']).rolling(20).mean().iloc[-1]

        effort = "HIGH" if last_v > avg_v * 1.5 else ("NORMAL" if last_v > avg_v else "LOW")
        result = "STRONG" if spread > avg_s * 1.5 else ("NORMAL" if spread > avg_s else "WEAK")

        anomaly = False
        if effort == "HIGH" and result == "WEAK":
            anomaly = "ABSORPTION"
        elif effort == "LOW" and result == "STRONG":
            anomaly = "EASE_OF_MOVEMENT"

        return {"effort": effort, "result": result, "anomaly": anomaly, "volume_ratio": last_v/avg_v if avg_v > 0 else 1.0}
