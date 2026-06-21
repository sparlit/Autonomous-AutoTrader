from typing import Optional, Dict, Any
import pandas as pd
from src.python.analyst.indicators import IndicatorAnalyst

class EMACross:
    def __init__(self):
        self.analyst = IndicatorAnalyst()

    def calculate_signal(self, df: pd.DataFrame) -> int:
        """Calculate signal based on EMA cross logic."""
        if len(df) < 20: return 0
        ema8 = df['c'].ewm(span=8).mean().iloc[-1]
        ema20 = df['c'].ewm(span=20).mean().iloc[-1]
        return 1 if ema8 > ema20 else -1

