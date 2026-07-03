import os
import asyncio
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.hive.config import load_config
from src.python.execution.risk_manager import RiskManager

try:
    import aat_institutional_core as aat_rust
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Market Data ingestion and normalization."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA_RAW":
            symbol = event.get("s")
            # V3.3.2: Precision key mapping with fallbacks
            bid = event.get("bi", event.get("b", 0))
            ask = event.get("as", event.get("a", 0))
            atr = event.get("atr", 0)
            ts = event.get("ts", event.get("tick_size", 0.0001))

            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "atr": atr,
                "spread": event.get("sp", 0),
                "tick_val": event.get("tv", 10.0),
                "tick_size": ts,
                "last_update": time.time()
            })

            return {"type": "MARKET_DATA", "symbol": symbol, "bid": bid, "ask": ask,
                    "atr": event.get("atr", 0), "ltf": event.get("ltf", []),
                    "m15": event.get("m15", []), "h1": event.get("h1", []),
                    "h4": event.get("h4", []), "d1": event.get("d1", [])}
        return None

class TrendBrain(BaseBrain):
    """
    Brain 3 - 10503: Multi-Timeframe Trend Evidence (V3.3.0-ASCENDANT).
    Mandatory: M15, H1, H4, D1.
    Rule: Majority (confluence) provided the TFs are consecutive.
    """
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

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
                else:
                    trends[tf] = "NEUTRAL"

            # Check consecutive majority
            bullish_pairs = 0
            bearish_pairs = 0

            if trends["m15"] == "BULLISH" and trends["h1"] == "BULLISH": bullish_pairs += 1
            if trends["h1"] == "BULLISH" and trends["h4"] == "BULLISH": bullish_pairs += 1
            if trends["h4"] == "BULLISH" and trends["d1"] == "BULLISH": bullish_pairs += 1

            if trends["m15"] == "BEARISH" and trends["h1"] == "BEARISH": bearish_pairs += 1
            if trends["h1"] == "BEARISH" and trends["h4"] == "BEARISH": bearish_pairs += 1
            if trends["h4"] == "BEARISH" and trends["d1"] == "BEARISH": bearish_pairs += 1

            direction = 0; # MANDATORY MTF CONFLUENCE
            p_e_h = 0.50; # Neutral posterior
            if bullish_pairs >= 2: direction = 1; p_e_h = 0.85
            elif bearish_pairs >= 2: direction = -1; p_e_h = 0.85
            elif bullish_pairs == 1: direction = 1; p_e_h = 0.70
            elif bearish_pairs == 1: direction = -1; p_e_h = 0.70

            self.ipc.set_state(f"trend_stats:{symbol}", trends)

            return {
                "type": "EVIDENCE", "symbol": symbol, "source": self.name,
                "direction": direction, "p_e_h": p_e_h, "p_e": 0.50,
                "data": {"trends": trends}
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Technical Indicator Evidence."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

            close = df['c']
            rsi = self.analyst.rsi(close)
            ema_fast = self.analyst.ema(close, 9)
            ema_slow = self.analyst.ema(close, 21)

            direction = 0
            if rsi > 55 and ema_fast > ema_slow: direction = 1
            elif rsi < 45 and ema_fast < ema_slow: direction = -1

            return {
                "type": "EVIDENCE", "symbol": event["symbol"], "source": self.name,
                "direction": direction, "p_e_h": 0.75, "p_e": 0.50,
                "data": {"rsi": rsi, "atr": event.get("atr", 0)}
            }
        return None

class RiskBrain(BaseBrain):
    """Brain 11 - 10517: Mandatory Vetting & Scaling Guard (V3.3.3 Assessment)."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]
            action = event["action"]

            # 1. Trading Lock Handled at Source (MetaBrain / PositionManager)

            # 2. Multi-Timeframe Assessment (Rule 1.b.i / 1.c.iii)
            trends = self.ipc.get_state(f"trend_stats:{symbol}", {})
            if not trends:
                return {"type": "VETO", "symbol": symbol, "reason": "STRICT_GUARD: NO TREND DATA"}

            required = "BULLISH" if action == "BUY" else "BEARISH"
            alignment = sum(1 for tf in ["m15", "h1", "h4", "d1"] if trends.get(tf) == required)

            if alignment < 3: # MANDATORY 3 OUT OF 4 ALIGNMENT
                return {"type": "VETO", "symbol": symbol, "reason": f"STRICT_GUARD: TREND MISALIGNED ({alignment}/4)"}

            # 3. Drawdown & Win Rate Assessment (Rule 1.b.iv/v/vi)
            stats = self.ipc.get_state("account_stats", {})
            reliability = self.ipc.get_state("brain_reliability", {})

            # Max Drawdown Assessment
            dd = stats.get("drawdown", 0)
            if dd > 5.0:
                return {"type": "VETO", "symbol": symbol, "reason": f"MAX_DRAWDOWN_BREACH: {dd:.2f}%"}

            # Bayesian Winning % Assessment
            avg_win_rate = sum(reliability.values()) / len(reliability) if reliability else 1.0
            if avg_win_rate < 0.40:
                 return {"type": "VETO", "symbol": symbol, "reason": f"LOW_SYSTEM_RELIABILITY: {avg_win_rate:.2f}"}

            # 4. Mandatory Risk & Probability Assessment (Rule 1.b.ii/iii)
            prob = event.get("probability", 0.5)
            if prob < 0.70: # Institutional Probability Floor
                 return {"type": "VETO", "symbol": symbol, "reason": f"INSUFFICIENT_PROBABILITY: {prob:.2f}"}

            # 5. Position & SL/TP Calculation (Rule 1.b.vii/viii/ix)
            event["lots"] = 0.01 # Always stable 0.01 lots
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            atr = event.get("atr") or s_stats.get("atr", 0)
            ts = s_stats.get("tick_size", 0.0001)

            if atr > 0 and ts > 0:
                sl_pts = int((atr * 2) / ts)
                tp_pts = sl_pts # 1:1 RR Unit
            else:
                # Institutional Fallback
                sl_pts = 5000 if "ETH" in symbol else (1000 if "JPY" in symbol or "XAU" in symbol else 200)
                tp_pts = sl_pts

            # Possibility of Loss Assessment (Noise vs SL)
            if atr > 0 and sl_pts * ts < atr * 1.5:
                return {"type": "VETO", "symbol": symbol, "reason": f"HIGH_POSSIBILITY_OF_LOSS: Noise risk"}

            event["sl_pts"] = max(50, sl_pts)
            event["tp_pts"] = max(50, tp_pts)

            # Debug Logging for Institutional Review
            try:
                if not os.path.exists("logs"): os.makedirs("logs")
                with open("logs/brain_decisions.log", "a") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - VETTED: {symbol} {action} L:{event['lots']} P:{prob:.2f} SL:{event['sl_pts']}\n")
            except: pass

            return {**event, "type": "VALIDATED_TRADE"}
        return None

class ExecutionBrain(BaseBrain):
    """Brain 12 - 10512: Final Order formatting for MT5."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            return {
                "type": "EXECUTION_ORDER", "t": "DEC", "s": event["symbol"],
                "act": event["action"], "lts": 0.01,
                "sl_p": event.get("sl_pts", 100), "tp_p": event.get("tp_pts", 100),
                "reason": event.get("reason", "BRAIN_SIGNAL")
            }
        return None

class AnomalyBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class PortfolioBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MonitoringBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class LiquidityBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class RegimeBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            return {"type": "REGIME_STATUS", "symbol": event["symbol"], "source": self.name, "regime": "TRENDING"}
        return None

class ContrarianBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class NewsRiskBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MemoryBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class CorrelationBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class SwingMaster(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class ScalpMaster(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class VSAMaster(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class WyckoffMaster(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class ICTKillzone(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class MomentumBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

class StructureBrain(BaseBrain):
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
