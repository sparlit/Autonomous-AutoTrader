import pandas as pd
import numpy as np
from typing import Dict, Any

class VolatilityAnalyst:
    def is_spread_safe(self, current_spread: float, avg_spread: float, threshold_multiplier: float = 2.0) -> bool:
        return current_spread <= (avg_spread * threshold_multiplier)

    def get_regime(self, df: pd.DataFrame) -> str:
        atr = (df['h'] - df['l']).rolling(20).mean()
        curr_atr = atr.iloc[-1]
        avg_atr = atr.mean()
        if curr_atr > avg_atr * 1.5: return "HIGH_VOLATILITY"
        elif curr_atr < avg_atr * 0.5: return "LOW_VOLATILITY"
        return "NORMAL"

    def analyze_vsa(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Volume Spread Analysis: Effort vs Result."""
        if len(df) < 20: return {"effort": "NEUTRAL", "result": "NEUTRAL", "anomaly": False, "volume_ratio": 1.0}

        avg_volume = df['v'].rolling(20).mean().iloc[-1]
        last_volume = df['v'].iloc[-1]
        spread = abs(df['c'].iloc[-1] - df['o'].iloc[-1])
        avg_spread = abs(df['c'] - df['o']).rolling(20).mean().iloc[-1]

        effort = "LOW"
        if last_volume > avg_volume * 1.5: effort = "HIGH"
        elif last_volume > avg_volume: effort = "NORMAL"

        result = "WEAK"
        if spread > avg_spread * 1.5: result = "STRONG"
        elif spread > avg_spread: result = "NORMAL"

        anomaly = False
        if effort == "HIGH" and result == "WEAK":
            anomaly = "ABSORPTION"

        return {"effort": effort, "result": result, "anomaly": anomaly, "volume_ratio": last_volume/avg_volume}
