from typing import Any
import pandas as pd
import numpy as np
import sys
import os
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

# 20100: Unified Institutional Rust Core Import
try:
    import aat_institutional_core as aat_rust
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

class SwingMaster(BaseBrain):
    """
    Institutional Swing Trading Strategy.
    Alignment: D1/H4 Trend.
    Filter: RSI Overextension (via Rust Veto + Dynamic Bands).
    Magic: 20101
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20101

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20102"""
        history = data.get("history", []) # Primary (H4)
        d1_raw = data.get("d1", [])

        if not history or len(history) < 50: return None

        df_h4 = pd.DataFrame(history)
        last_close = df_h4['c'].iloc[-1]
        ema_50_h4 = df_h4['c'].ewm(span=50).mean().iloc[-1]
        trend_h4 = 1 if last_close > ema_50_h4 else -1

        delta = df_h4['c'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        loss = loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + gain / loss))
        curr_rsi = rsi.iloc[-1]

        # 20105: Dynamic ATR-relative RSI Bands
        high = df_h4['h']; low = df_h4['l']; cp = df_h4['c'].shift(1)
        tr = pd.concat([high-low, (high-cp).abs(), (low-cp).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

        # Volatility-adjusted overextension band
        vol_ratio = (atr / last_close) * 100
        overextension_band = max(5, min(15, 10 / vol_ratio)) if vol_ratio > 0 else 10

        upper_limit = 100 - overextension_band
        lower_limit = overextension_band

        direction = 0
        confidence = 0.0

        # Trend D1 Calculation
        if d1_raw:
            df_d1 = pd.DataFrame(d1_raw)
            ema_200_d1 = df_d1['c'].ewm(span=200).mean().iloc[-1]
            trend_d1 = 1 if df_d1['c'].iloc[-1] > ema_200_d1 else -1
        else:
            ema_200_h4 = df_h4['c'].ewm(span=200).mean().iloc[-1]
            trend_d1 = 1 if last_close > ema_200_h4 else -1

        if RUST_AVAILABLE:
            if aat_rust.validate_swing_setup_fast(trend_h4, trend_d1, curr_rsi):
                # Additional Python-side dynamic check
                if (trend_h4 == 1 and curr_rsi > upper_limit) or (trend_h4 == -1 and curr_rsi < lower_limit):
                    direction = 0
                else:
                    direction = trend_h4
                    confidence = 0.8
        else:
            if trend_h4 == trend_d1:
                if (trend_h4 == 1 and curr_rsi < upper_limit) or (trend_h4 == -1 and curr_rsi > lower_limit):
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
