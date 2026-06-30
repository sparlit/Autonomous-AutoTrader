import asyncio
import logging
import time
import pandas as pd
import numpy as np
import aiosqlite
from typing import Dict, Any, List, Optional
from src.python.brains.base import BaseBrain
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from src.python.execution.risk_manager import RiskManager
from src.python.hive.config import load_config

# Institutional Rust Core for VaR
try:
    import aat_institutional_core as aat_rust
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

logger = logging.getLogger("AAT_SpecializedBrains")

class MarketDataBrain(BaseBrain):
    """Brain 1 - 10501: Data Ingestion and Normalization."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "DP":
            # 10502: Pass through tick metrics for precise exposure calculation
            return {
                "type": "MARKET_DATA", "symbol": event["s"], "tf": event["tf"],
                "ltf": event["ltf"], "h1": event["h1"], "h4": event["h4"],
                "bid": event["bi"], "ask": event["as"], "atr": event.get("atr", 0),
                "tick_val": event.get("tv", 10.0), "tick_size": event.get("ts", 0.0001)
            }
        return None

class IndicatorBrain(BaseBrain):
    """Brain 2 - 10502: Technical Indicator Evidence (Trend/RSI)."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            inds = self.analyst.calculate_all(df)

            # Update symbol stats with realized vol for PortfolioBrain
            symbol = event["symbol"]
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {"symbol": symbol})
            s_stats.update({
                "realized_vol": inds.get("realized_vol", 0.002),
                "tick_val": event.get("tick_val", 10.0),
                "tick_size": event.get("tick_size", 0.0001)
            })
            self.ipc.set_state(f"symbol_stats:{symbol}", s_stats)

            rsi = inds["rsi"]
            evidence = {"type": "EVIDENCE", "symbol": symbol, "source": self.name, "data": inds}
            if rsi > 60: evidence.update({"p_e_h": 0.65, "p_e": 0.50, "direction": 1})
            elif rsi < 40: evidence.update({"p_e_h": 0.65, "p_e": 0.50, "direction": -1})
            else: evidence.update({"p_e_h": 0.50, "p_e": 0.50, "direction": 0})
            return evidence
        return None

class MomentumBrain(BaseBrain):
    """Brain 12 - 10517: Advanced Momentum Evidence (MACD/ADX)."""
    async def initialize(self):
        await super().initialize()
        self.analyst = IndicatorAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            inds = self.analyst.calculate_all(df)

            direction = 0
            if inds["macd_hist"] > 0 and inds["adx"] > 25: direction = 1
            elif inds["macd_hist"] < 0 and inds["adx"] > 25: direction = -1

            return {
                "type": "MOMENTUM_STATUS",
                "symbol": event["symbol"],
                "source": self.name,
                "direction": direction,
                "adx": inds["adx"],
                "macd": inds["macd_hist"]
            }
        return None

class TrendBrain(BaseBrain):
    """Brain 3 - 10503: Market Structure Evidence."""
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            struct = self.smc.detect_market_structure(df)

            h1_df = pd.DataFrame(event.get("h1", []))
            h4_df = pd.DataFrame(event.get("h4", []))
            aligned = 0
            if not h1_df.empty:
                if isinstance(event["h1"][0], list): h1_df.columns = ["o", "h", "l", "c", "t", "v"]
                if self.smc.detect_market_structure(h1_df)["trend"] == struct["trend"]: aligned += 1
            if not h4_df.empty:
                if isinstance(event["h4"][0], list): h4_df.columns = ["o", "h", "l", "c", "t", "v"]
                if self.smc.detect_market_structure(h4_df)["trend"] == struct["trend"]: aligned += 1

            direction = 1 if struct["trend"] == "BULLISH" else (-1 if struct["trend"] == "BEARISH" else 0)
            evidence = {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "direction": direction}
            if aligned == 2: evidence.update({"p_e_h": 0.85, "p_e": 0.45})
            elif aligned == 1: evidence.update({"p_e_h": 0.70, "p_e": 0.55})
            else: evidence.update({"p_e_h": 0.60, "p_e": 0.60})
            return evidence
        return None

class StructureBrain(BaseBrain):
    """Brain 13 - 10518: SMC Structural Elements (FVG/IDM)."""
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]

            fvgs = self.smc.detect_fvg(df)
            idm = self.smc.detect_inducement(df)
            trigger = self.smc.detect_candlestick_trigger(df)

            return {
                "type": "STRUCTURE_STATUS",
                "symbol": event["symbol"],
                "source": self.name,
                "fvgs": len(fvgs),
                "idm": idm["type"] if idm else "NONE",
                "trigger": trigger or "NONE"
            }
        return None

class LiquidityBrain(BaseBrain):
    """Brain 4 - 10505: Order Block Evidence."""
    async def initialize(self):
        await super().initialize()
        self.smc = SMCAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            obs = self.smc.detect_order_blocks(df)
            if not obs: return None
            latest_ob = obs[-1]
            return {"type": "EVIDENCE", "symbol": event["symbol"], "source": self.name, "direction": 1 if latest_ob["type"] == "BULLISH" else -1, "p_e_h": 0.80, "p_e": 0.60}
        return None

class RegimeBrain(BaseBrain):
    """Brain - 10506: Volatility Regime Status."""
    async def initialize(self):
        await super().initialize()
        self.volatility = VolatilityAnalyst()

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            regime = self.volatility.get_regime(df)
            return {"type": "REGIME_STATUS", "symbol": event["symbol"], "source": self.name, "regime": regime}
        return None

class ContrarianBrain(BaseBrain):
    """Brain - 10507: Veto logic."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            if event.get("atr", 0) < 0.00005:
                return {"type": "VETO", "symbol": event["symbol"], "reason": "ATR_TOO_LOW"}
        return None

class NewsRiskBrain(BaseBrain):
    """Brain - 10509: News safety veto."""
    async def initialize(self):
        await super().initialize()
        self.risk_manager = RiskManager(load_config())

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.risk_manager.is_news_safe():
            return {"type": "NEWS_VETO", "symbol": event.get("symbol", "GLOBAL"), "reason": "NEWS_WINDOW"}
        return None

class MemoryBrain(BaseBrain):
    """Brain - 12501: Continuous Learning and Calibration."""
    async def initialize(self):
        await super().initialize()
        self.reliabilities: Dict[str, float] = {}

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        e_type = event.get("type")
        if e_type == "TRADE_CLOSED":
            symbol = event["symbol"]; outcome = event["outcome"]
            evidence_trail = event.get("evidence_trail", [])
            for entry in evidence_trail:
                source = entry["source"]
                correct = (entry["direction"] == 1 and outcome == "WIN") or (entry["direction"] == -1 and outcome == "WIN")
                curr = self.reliabilities.get(source, 1.0)
                adjustment = 0.05 if correct else -0.05
                self.reliabilities[source] = max(0.1, min(2.0, curr + adjustment))
            return {"type": "RELIABILITY_REPORT", "scores": self.reliabilities}
        elif e_type == "RELIABILITY_REQUEST":
            return {"type": "RELIABILITY_REPORT", "scores": self.reliabilities}
        return None

class RiskBrain(BaseBrain):
    """Brain 6 - 10512: Probabilistic Position Sizing."""
    async def initialize(self):
        await super().initialize()
        self.risk_manager = RiskManager(load_config())
        self.execution_score = 0.95

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]; prob = event["probability"]
            if prob < 0.55: return None
            regime_score = 1.0 if event.get("regime") == "TRENDING_FAST" else (0.8 if "TRENDING" in event.get("regime", "") else 0.5)
            v = self.risk_manager.validate_trade(symbol, event["action"], 1000.0, atr=event["atr"])
            if v["safe"]:
                prob_mult = (prob - 0.50) / 0.45
                final_lots = round(v["lots"] * prob_mult * regime_score * self.execution_score, 2)
                if final_lots < 0.01: return None
                return {"type": "VALIDATED_TRADE", "symbol": symbol, "action": event["action"], "lots": final_lots, "sl_pts": v["sl_pts"], "tp_pts": v["tp_pts"], "probability": prob, "evidence_trail": event.get("evidence_trail", [])}
        return None

class ExecutionBrain(BaseBrain):
    """Brain 7 - 10513: Actuation."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "VALIDATED_TRADE":
            return {
                "type": "EXECUTION_ORDER", "t": "DEC", "id": int(time.time()), "s": event["symbol"],
                "act": event["action"], "lts": event["lots"], "sl_p": event["sl_pts"], "tp_p": event["tp_pts"],
                "evidence_trail": event.get("evidence_trail")
            }
        return None

class AnomalyBrain(BaseBrain):
    """Brain 8 - 10514: Flash Crash and Spike Detection."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "MARKET_DATA":
            df = pd.DataFrame(event.get("ltf", []))
            if df.empty or len(df) < 2: return None
            if isinstance(event["ltf"][0], list): df.columns = ["o", "h", "l", "c", "t", "v"]
            price_change_pct = abs(df['c'].iloc[-1] - df['o'].iloc[-1]) / df['o'].iloc[-1]
            if price_change_pct > 0.02:
                return {"type": "ANOMALY_STATUS", "symbol": event["symbol"], "anomaly": "SPIKE", "severity": "HIGH"}
        return None

class PortfolioBrain(BaseBrain):
    """Brain 9 - 10515: Global Risk and Capital Allocation with Institutional VaR."""
    async def initialize(self):
        await super().initialize()
        self.risk_manager = RiskManager(load_config())
        self.last_var_check = 0

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("t") == "HB":
            drawdown = event.get("dd", 0)
            if drawdown > self.risk_manager.config.risk.max_drawdown_pct:
                return {"type": "VETO", "symbol": "GLOBAL", "reason": "MAX_DRAWDOWN"}

        # 10520: Real-time Institutional VaR Calculation
        now = time.time()
        if now - self.last_var_check > 5: # Check every 5 seconds
            self.last_var_check = now
            active_trades = self.ipc.get_state("active_trades", [])
            if active_trades and RUST_AVAILABLE:
                exposures = []
                vols = []
                for t in active_trades:
                    # 10521: Accurate Exposure via Symbol Metrics
                    s_stats = self.ipc.get_state(f"symbol_stats:{t['symbol']}", {})
                    tick_val = s_stats.get("tick_val", 10.0)
                    tick_size = s_stats.get("tick_size", 0.0001)

                    # Exposure = (lots * tick_val) / tick_size
                    # This represents the monetary value of the full position
                    if tick_size > 0:
                        exposure = (t['lots'] * tick_val) / tick_size
                    else:
                        exposure = t['lots'] * 100000 * t['entry_price']

                    exposures.append(exposure)
                    vols.append(s_stats.get("realized_vol", 0.002))

                portfolio_var = aat_rust.calculate_var_parallel(exposures, vols)
                equity = self.ipc.get_state("account_stats", {}).get("equity", 10000)
                var_pct = (portfolio_var / equity) * 100 if equity > 0 else 0

                self.ipc.set_state("portfolio_var", {"value": portfolio_var, "pct": var_pct})

                if var_pct > 5.0:
                    return {"type": "VETO", "symbol": "GLOBAL", "reason": f"VAR_LIMIT_EXCEEDED_{var_pct:.2f}%"}

        return None

class MonitoringBrain(BaseBrain):
    """Brain 10 - 10516: System Health Monitoring."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "HEALTH_CHECK":
            return {"type": "HEALTH_REPORT", "status": "OPTIMAL", "timestamp": time.time()}
        return None

class CorrelationBrain(BaseBrain):
    """Brain 14 - 10519: Cross-symbol correlation analysis."""
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # 10520: Multi-pair correlation check to prevent over-exposure
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]
            # 10521: Consistently handle active_trades as a LIST
            active_trades = self.ipc.get_state("active_trades", [])
            if "EURUSD" in symbol and any("GBPUSD" in t['symbol'] for t in active_trades):
                return {"type": "VETO", "symbol": symbol, "reason": "HIGH_CORRELATION_GBPUSD"}
        return None
