import pandas as pd
import numpy as np
from typing import Dict, Any

class VolatilityAnalyst:
    def __init__(self):
        """Magic: 8200"""
        self.magic = 8200

    def is_spread_safe(self, current_spread: float, avg_spread: float, threshold_multiplier: float = 2.0) -> bool:
        """Magic: 8201"""
        return current_spread <= (avg_spread * threshold_multiplier)

    def get_regime(self, df: pd.DataFrame) -> str:
        """Magic: 8202"""
        if len(df) < 20: return "NORMAL"
        atr = (df['h'] - df['l']).rolling(20).mean()
        curr_atr = atr.iloc[-1]
        avg_atr = atr.mean()
        if curr_atr > avg_atr * 1.5: return "HIGH_VOLATILITY"
        elif curr_atr < avg_atr * 0.5: return "LOW_VOLATILITY"
        return "NORMAL"

    def analyze_vsa(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Magic: 8203"""
        if len(df) < 20: return {"effort": "NEUTRAL", "result": "NEUTRAL", "anomaly": False, "volume_ratio": 1.0, "m_id": 8203}
        avg_v = df['v'].rolling(20).mean().iloc[-1]
        last_v = df['v'].iloc[-1]
        spread = abs(df['c'].iloc[-1] - df['o'].iloc[-1])
        avg_s = abs(df['c'] - df['o']).rolling(20).mean().iloc[-1]
        avg_v = max(avg_v, 1e-9); avg_s = max(avg_s, 1e-9)

        effort = "HIGH" if last_v > avg_v * 1.5 else ("NORMAL" if last_v > avg_v else "LOW")
        result = "STRONG" if spread > avg_s * 1.5 else ("NORMAL" if spread > avg_s else "WEAK")
        anomaly = "ABSORPTION" if effort == "HIGH" and result == "WEAK" else False
        return {"effort": effort, "result": result, "anomaly": anomaly, "volume_ratio": float(last_v/avg_v), "m_id": 8203}
