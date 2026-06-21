import pandas as pd
import numpy as np
import sys
import os
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

# Import Rust Core for high-speed veto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../bridge'))
try:
    import aat_rust_core
    RUST_CORE_AVAILABLE = True
except ImportError:
    RUST_CORE_AVAILABLE = False

class SwingMaster(BaseBrain):
    """
    Institutional Swing Trading Strategy.
    Alignment: D1/H4 Trend.
    Filter: RSI Overextension (via Rust Veto).
    Magic: 20101
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.magic = 20101

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20102"""
        history = data.get("history", []) # Primary (H4)
        h1_raw = data.get("h1", [])
        h4_raw = data.get("h4", [])

        if not history or len(history) < 50: return None

        df_h4 = pd.DataFrame(history)
        ema_50_h4 = df_h4['c'].ewm(span=50).mean().iloc[-1]
        trend_h4 = 1 if df_h4['c'].iloc[-1] > ema_50_h4 else -1

        delta = df_h4['c'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        loss = loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + gain / loss))
        curr_rsi = rsi.iloc[-1]

        direction = 0
        confidence = 0.0

        ema_200_h4 = df_h4['c'].ewm(span=200).mean().iloc[-1]
        trend_d1_proxy = 1 if df_h4['c'].iloc[-1] > ema_200_h4 else -1

        if RUST_CORE_AVAILABLE:
            if aat_rust_core.validate_swing_setup_fast(trend_h4, trend_d1_proxy, curr_rsi):
                direction = trend_h4
                confidence = 0.8
        else:
            if trend_h4 == trend_d1_proxy:
                if (trend_h4 == 1 and curr_rsi < 70) or (trend_h4 == -1 and curr_rsi > 30):
                    direction = trend_h4
                    confidence = 0.7

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=confidence,
            strategy_name=self.name,
            magic=self.magic
        )
