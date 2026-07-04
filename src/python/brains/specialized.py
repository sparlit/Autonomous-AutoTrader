import os
import asyncio
import logging
import time
import pandas as pd
import numpy as np
import os
import json
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst

logger = logging.getLogger("AAT_Brains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Data Normalization & Broadcast."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP":
            symbol = event["s"]
            # 10502: Harden state with explicit defaults to prevent None arithmetic in other brains
            bid = float(event.get("b") or 0.0)
            ask = float(event.get("a") or 0.0)
            atr = float(event.get("atr") or 0.0)
            sp = float(event.get("sp") or 0.0)
            tv = float(event.get("tv") or 10.0)
            ts = float(event.get("ts") or 0.0001)

            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "tick_val": tv, "tick_size": ts,
                "atr": atr, "spread": sp
            })
            return {"type": "MARKET_DATA", "symbol": symbol, "bid": bid, "ask": ask,
                    "atr": atr, "sp": sp,
                    "ltf": event.get("ltf", []), "m15": event.get("m15", []), "h1": event.get("h1", []),
                    "h4": event.get("h4", []), "d1": event.get("d1", [])}
        return None

class TrendBrain(BaseBrain):
    """Brain 3 - 10503: Multi-Timeframe Trend Evidence."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            symbol = event["symbol"]
            tfs = ["m15", "h1", "h4", "d1"]
            trends = {}
            for tf in tfs:
                df = pd.DataFrame(event.get(tf, []))
                if not df.empty:
                    if isinstance(event[tf][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
                    trends[tf] = self.smc.detect_market_structure(df)["trend"]
                else: trends[tf] = "NEUTRAL"

            bullish_pairs = (1 if trends.get("m15") == "BULLISH" and trends.get("h1") == "BULLISH" else 0) +                             (1 if trends.get("h1") == "BULLISH" and trends.get("h4") == "BULLISH" else 0) +                             (1 if trends.get("h4") == "BULLISH" and trends.get("d1") == "BULLISH" else 0)
            bearish_pairs = (1 if trends.get("m15") == "BEARISH" and trends.get("h1") == "BEARISH" else 0) +                             (1 if trends.get("h1") == "BEARISH" and trends.get("h4") == "BEARISH" else 0) +                             (1 if trends.get("h4") == "BEARISH" and trends.get("d1") == "BEARISH" else 0)

            direction = 0; p_e_h = 0.50
            if bullish_pairs >= 2: direction = 1; p_e_h = 0.85
            elif bearish_pairs >= 2: direction = -1; p_e_h = 0.85
            elif bullish_pairs == 1: direction = 1; p_e_h = 0.70
            elif bearish_pairs == 1: direction = -1; p_e_h = 0.70

            self.ipc.set_state(f"trend_stats:{symbol}", trends)
            self.publish_state(symbol, {"trends": trends, "dir": direction, "p_e_h": p_e_h})

            return {"type": "EVIDENCE", "symbol": symbol, "source": self.name,
                    "direction": direction, "p_e_h": p_e_h, "p_e": 0.50, "data": {"trends": trends}}
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Technical Indicator Evidence."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            symbol = event["symbol"]
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            close = df['c']; rsi = self.analyst.rsi(close)
            ema9 = self.analyst.ema(close, 9); ema21 = self.analyst.ema(close, 21)

            # Robust comparison
            rsi_val = float(rsi) if not isinstance(rsi, pd.Series) else float(rsi.iloc[-1] if not rsi.empty else 50.0)
            e9_val = float(ema9.iloc[-1]) if not ema9.empty else 0.0
            e21_val = float(ema21.iloc[-1]) if not ema21.empty else 0.0

            direction = 1 if (rsi_val > 55 and e9_val > e21_val) else (-1 if (rsi_val < 45 and e9_val < e21_val) else 0)

            self.publish_state(symbol, {"rsi": rsi_val, "ema9": e9_val, "ema21": e21_val, "dir": direction})
            return {"type": "EVIDENCE", "symbol": symbol, "source": self.name,
                    "direction": direction, "p_e_h": 0.75, "p_e": 0.50, "data": {"rsi": rsi_val}}
        return None

class RiskBrain(BaseBrain):
    """Brain 11 - 10517: Mandatory Vetting & Scaling Guard."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]; action = event["action"]
            trends = self.ipc.get_state(f"trend_stats:{symbol}", {})
            if not trends:
                self.publish_state(symbol, {"veto": True, "reason": "NO TREND DATA"})
                return {"type": "VETO", "symbol": symbol, "reason": "STRICT_GUARD: NO TREND DATA"}

            required = "BULLISH" if action == "BUY" else "BEARISH"
            alignment = sum(1 for tf in ["m15", "h1", "h4", "d1"] if trends.get(tf) == required)
            if alignment < 3:
                self.publish_state(symbol, {"veto": True, "reason": f"TREND MISALIGNED ({alignment}/4)"})
                return {"type": "VETO", "symbol": symbol, "reason": f"STRICT_GUARD: TREND MISALIGNED ({alignment}/4)"}

            stats = self.ipc.get_state("account_stats", {}); rel = self.ipc.get_state("brain_reliability", {})
            dd = float(stats.get("drawdown") or 0.0)
            if dd > 5.0:
                self.publish_state(symbol, {"veto": True, "reason": f"DD BREACH {dd:.2f}%"})
                return {"type": "VETO", "symbol": symbol, "reason": f"MAX_DRAWDOWN_BREACH: {dd:.2f}%"}

            avg_win = sum(rel.values()) / len(rel) if rel else 1.0
            if avg_win < 0.40:
                 self.publish_state(symbol, {"veto": True, "reason": f"LOW RELIABILITY {avg_win:.2f}"})
                 return {"type": "VETO", "symbol": symbol, "reason": f"LOW_SYSTEM_RELIABILITY: {avg_win:.2f}"}

            prob = float(event.get("probability") or 0.5)
            if prob < 0.70:
                 self.publish_state(symbol, {"veto": True, "reason": f"LOW PROB {prob:.2f}"})
                 return {"type": "VETO", "symbol": symbol, "reason": f"INSUFFICIENT_PROBABILITY: {prob:.2f}"}

            event["lots"] = 0.01; s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            atr = float(event.get("atr") or s_stats.get("atr") or 0.0)
            ts = float(s_stats.get("tick_size") or 0.0001)

            if atr > 0 and ts > 0: sl_pts = int((atr * 2) / ts); tp_pts = sl_pts
            else: sl_pts = 200; tp_pts = 200

            if atr > 0 and sl_pts * ts < atr * 1.5:
                self.publish_state(symbol, {"veto": True, "reason": "NOISE RISK"})
                return {"type": "VETO", "symbol": symbol, "reason": f"HIGH_POSSIBILITY_OF_LOSS: Noise risk"}

            event["sl_pts"] = max(50, sl_pts); event["tp_pts"] = max(50, tp_pts)
            self.publish_state(symbol, {"validated": True, "sl": event["sl_pts"], "tp": event["tp_pts"], "prob": prob})
            return {**event, "type": "VALIDATED_TRADE"}
        return None

class ExecutionBrain(BaseBrain):
    """Brain 12 - 10512: Final Order formatting."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            res = {"type": "EXECUTION_ORDER", "t": "DEC", "s": event["symbol"], "act": event["action"], "lts": 0.01,
                   "sl_p": float(event.get("sl_pts", 100)), "tp_p": float(event.get("tp_pts", 100)), "reason": event.get("reason", "BRAIN_SIGNAL")}
            self.publish_state(event["symbol"], {"executed": True, "order": res})
            return res
        return None

class AnomalyBrain(BaseBrain):
    async def process(self, e):
        if e.get("type") == "MARKET_DATA": self.publish_state(e["symbol"], {"status": "SCANNING", "anomaly": False})
        return None
class PortfolioBrain(BaseBrain):
    async def process(self, e):
        return None
class MonitoringBrain(BaseBrain):
    async def process(self, e):
        return None
class LiquidityBrain(BaseBrain):
    async def process(self, e):
        return None
class RegimeBrain(BaseBrain):
    async def process(self, e):
        if e.get("type") == "MARKET_DATA": self.publish_state(e["symbol"], {"regime": "TRENDING"})
        return None
class ContrarianBrain(BaseBrain):
    async def process(self, e):
        return None
class NewsRiskBrain(BaseBrain):
    async def process(self, e):
        return None
class MemoryBrain(BaseBrain):
    async def process(self, e):
        return None
class CorrelationBrain(BaseBrain):
    async def process(self, e):
        return None
class SwingMaster(BaseBrain):
    async def process(self, e):
        return None
class ScalpMaster(BaseBrain):
    async def process(self, e):
        return None
class VSAMaster(BaseBrain):
    async def process(self, e):
        return None
class WyckoffMaster(BaseBrain):
    async def process(self, e):
        return None
class ICTKillzone(BaseBrain):
    async def process(self, e):
        return None
class MomentumBrain(BaseBrain):
    async def process(self, e):
        return None
class StructureBrain(BaseBrain):
    async def process(self, e):
        return None
