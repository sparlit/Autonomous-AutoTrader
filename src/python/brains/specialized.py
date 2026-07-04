import os
import asyncio
import logging
import time
import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional, Union
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst

logger = logging.getLogger("AAT_Brains")

class MarketDataBrain(BaseBrain):
    """V4.0: High-throughput Data Normalization."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP":
            symbol = event["s"]
            bid = float(event.get("b") or 0.0)
            ask = float(event.get("a") or 0.0)
            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "tick_val": float(event.get("tv", 10.0)),
                "tick_size": float(event.get("ts", 0.0001)),
                "atr": float(event.get("atr", 0.0)),
                "spread": float(event.get("sp", 0.0))
            })
            return {
                "type": "MARKET_DATA", "symbol": symbol, "bid": bid, "ask": ask,
                "atr": float(event.get("atr", 0.0)), "sp": float(event.get("sp", 0.0)),
                "ltf": event.get("ltf", []),
                "mtf": event.get("mtf", {})
            }
        return None

class TrendBrain(BaseBrain):
    """V4.0: Parallel MTF Trend Assessment (M1-MN1)."""
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            symbol = event["symbol"]
            mtf_data = event.get("mtf", {})
            tfs = ["m1", "m5", "m15", "m30", "h1", "h4", "d1", "w1", "mn1"]
            trends = {}
            for tf in tfs:
                df_data = mtf_data.get(tf, [])
                if df_data:
                    df = pd.DataFrame(df_data)
                    if not df.empty:
                        if isinstance(df_data[0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
                        trends[tf] = self.smc.detect_market_structure(df)["trend"]
                    else: trends[tf] = "NEUTRAL"
                else: trends[tf] = "NEUTRAL"

            tf_weights = {"m1": 0.5, "m5": 0.7, "m15": 1.0, "m30": 1.2, "h1": 1.5, "h4": 2.0, "d1": 2.5, "w1": 3.0, "mn1": 4.0}
            score = 0.0
            for tf, weight in tf_weights.items():
                t = trends.get(tf, "NEUTRAL")
                if t == "BULLISH": score += weight
                elif t == "BEARISH": score -= weight

            direction = 1 if score > 5.0 else (-1 if score < -5.0 else 0)
            p_e_h = min(0.95, 0.5 + (abs(score) / 20.0))
            self.ipc.set_state(f"trend_stats:{symbol}", trends)
            return {"type": "EVIDENCE", "symbol": symbol, "source": self.name,
                    "direction": direction, "p_e_h": p_e_h, "p_e": 0.50, "data": {"trends": trends, "score": score}}
        return None

class IndicatorBrain(BaseBrain):
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            symbol = event["symbol"]
            ltf = event.get("ltf", [])
            if not ltf: return None
            df = pd.DataFrame(ltf)
            if isinstance(ltf[0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            rsi = self.analyst.rsi(df['c'])
            return {"type": "EVIDENCE", "symbol": symbol, "source": self.name,
                    "direction": 1 if rsi > 55 else (-1 if rsi < 45 else 0), "p_e_h": 0.75, "p_e": 0.50}
        return None

class RiskBrain(BaseBrain):
    """V4.0: Dynamic Position Sizing & vRR (Variable Risk-to-Reward)."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]
            action = event["action"]

            # 1. Institutional Constraints
            stats = self.ipc.get_state("account_stats", {})
            if float(stats.get("drawdown", 0)) > 5.0: return {"type": "VETO", "symbol": symbol, "reason": "MAX_DD"}

            # 2. Variable Risk-to-Reward (vRR)
            # Use ADX to determine regime strength
            trends = self.ipc.get_state(f"trend_stats:{symbol}", {})
            regime_strength = sum(1 for tf in trends.values() if (tf == "BULLISH" if action == "BUY" else "BEARISH"))

            # 1:1.5 for weak confluence, 1:3 for strong MTF alignment
            rr_ratio = 1.5 if regime_strength < 5 else 3.0

            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            atr = float(s_stats.get("atr") or 0.0)
            ts = float(s_stats.get("tick_size") or 0.0001)

            if atr > 0:
                sl_pts = int((atr * 2) / ts)
                tp_pts = int(sl_pts * rr_ratio)
            else:
                sl_pts = 200; tp_pts = int(200 * rr_ratio)

            return {
                **event,
                "type": "VALIDATED_TRADE",
                "lots": 0.01,
                "sl_pts": max(50, sl_pts),
                "tp_pts": max(50, tp_pts),
                "rr_ratio": rr_ratio
            }
        return None

class ExecutionBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            return {"type": "EXECUTION_ORDER", "t": "DEC", "s": event["symbol"], "act": event["action"],
                   "lts": event["lots"], "sl_p": float(event["sl_pts"]), "tp_p": float(event["tp_pts"])}
        return None

class MomentumBrain(BaseBrain):
    async def process(self, e): return None
class StructureBrain(BaseBrain):
    async def process(self, e): return None
class RegimeBrain(BaseBrain):
    async def process(self, e): return None
