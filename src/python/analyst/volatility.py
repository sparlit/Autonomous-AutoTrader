import pandas as pd
import numpy as np
from typing import Dict, Any

class VolatilityAnalyst:
    """12007: Volume-Spread and market regime analysis."""
    def is_spread_safe(self, current_spread: float, avg_spread: float, threshold_multiplier: float = 2.0) -> bool:
        """12008: Spread safety check."""
        return current_spread <= (avg_spread * threshold_multiplier)

    def get_regime(self, df: pd.DataFrame) -> str:
        """12009: Multi-regime classification (Trending, Ranging, High/Low Vol)."""
        if len(df) < 20: return "NORMAL"
        atr = (df['h'] - df['l']).rolling(20).mean()
        curr_atr = atr.iloc[-1]
        avg_atr = atr.mean()

        # 12010: ADX-based trendiness
        # Since ADX is not here, we use a simple price distance / ATR ratio
        price_range = abs(df['c'].iloc[-1] - df['c'].iloc[-20])
        trendiness = price_range / (curr_atr * 20)

        if curr_atr > avg_atr * 1.5: return "HIGH_VOLATILITY"
        if trendiness > 0.5: return "TRENDING"
        if curr_atr < avg_atr * 0.5: return "LOW_VOLATILITY"
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
        anomaly = "ABSORPTION" if effort == "HIGH" and result == "WEAK" else False
        return {"effort": effort, "result": result, "anomaly": anomaly, "volume_ratio": last_v/avg_v}
