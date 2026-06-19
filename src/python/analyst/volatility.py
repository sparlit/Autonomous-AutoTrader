import pandas as pd

class VolatilityAnalyst:
    def is_spread_safe(self, current_spread: float, avg_spread: float, threshold_multiplier: float = 2.0) -> bool:
        return current_spread <= (avg_spread * threshold_multiplier)

    def get_regime(self, df: pd.DataFrame) -> str:
        # Simple volatility-based regime detection
        atr = (df['h'] - df['l']).rolling(20).mean()
        curr_atr = atr.iloc[-1]
        avg_atr = atr.mean()

        if curr_atr > avg_atr * 1.5:
            return "HIGH_VOLATILITY"
        elif curr_atr < avg_atr * 0.5:
            return "LOW_VOLATILITY"
        return "NORMAL"
