import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorAnalyst:
    """12005: Vectorized technical analysis."""
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute technical indicators from OHLC market data.
        """
        c = df['c']
        ema100 = self.ema(c, 100)
        ema200 = self.ema(c, 200)
        macd_line, signal_line, hist = self.macd(c)
        adx = self.adx(df)
        atr = self.atr(df)

        # 12105: Realized Volatility for Institutional VaR
        # Annualized volatility of log returns
        log_returns = np.log(c / c.shift(1))
        realized_vol = log_returns.std() * np.sqrt(252 * 288) if len(log_returns) > 20 else 0.002

        return {
            "rsi": self.rsi(c),
            "atr": atr,
            "ema_fast": self.ema(c, 50),
            "ema_slow": ema200,
            "ema_100": ema100,
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_hist": hist,
            "adx": adx,
            "realized_vol": realized_vol
        }

    def rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(window=period).mean()
        ma_down = down.rolling(window=period).mean()
        rs = ma_up / ma_down
        return (100 - (100 / (1 + rs))).iloc[-1]

    def ema(self, series: pd.Series, period: int) -> float:
        return series.ewm(span=period, adjust=False).mean().iloc[-1]

    def atr(self, df: pd.DataFrame, period: int = 14) -> float:
        high = df['h']; low = df['l']; cp = df['c'].shift(1)
        tr = pd.concat([high-low, (high-cp).abs(), (low-cp).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def macd(self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line.iloc[-1], signal_line.iloc[-1], (macd_line - signal_line).iloc[-1]

    def adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """12017: Average Directional Index (ADX)."""
        h = df['h']; l = df['l']; c = df['c']
        upmove = h.diff(); downmove = l.diff()
        plus_dm = np.where((upmove > downmove) & (upmove > 0), upmove, 0)
        minus_dm = np.where((downmove > upmove) & (downmove > 0), downmove, 0)

        tr = pd.concat([h-l, (h-c.shift(1)).abs(), (l-c.shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        plus_di = 100 * (pd.Series(plus_dm).rolling(period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(period).mean() / atr)
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
        return dx.rolling(period).mean().iloc[-1]
