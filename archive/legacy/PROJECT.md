# 🌌 Project Autonomous AutoTrader (AAT)
**Internal Code-Name**: Phoenix Gauntlet
**Version**: V3.0-AUTONOMOUS (Institutional Pro)

## 📖 1. Project Identity & Vision
AAT operates under a Zero-Tolerance Standard for stubs and placeholders.
AAT is a high-probability, autonomous trading system engineered for MetaTrader 5, powered by a Python-based "Brain." It operates on the principle of **Defensive Alpha**: capital preservation is the primary objective; profit is a secondary outcome of discipline.

### 💎 Core Values (V3.0-AUTONOMOUS - Zero-Tolerance)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Python + MT5:** Leveraging the best of both ecosystems.

---

## 🛠️ 2. System Overview (V3.0 Evolution)
The system is built as a microkernel with event-driven decoupling, utilizing a **Multi-Brain Bayesian Orchestrator** pinned to 20 logical CPU cores.

### 🧩 Components
- **Python Hive (Coordinator):** Global risk management and Bayesian evidence aggregation.
- **Specialized Brains:** 20+ isolated processes (Market Data, Trend, Liquidity, Momentum, Regime, etc.).
- **Analyst Tier:** Vectorized SMC, VSA, and Technical Indicator engines.
- **MQL5 Agents:** Ultra-slim execution units with SYNC protocol and Heartbeat failsafes.
- **Persistence:** SQLite (Audit Ledger) and Redis Stream simulation (IPC).

---

## 🧠 3. Quantitative Strategy (Confluence Engine)
AAT V3.0 enforces a **3-of-4 Confluence Rule**:
1. **Trend**: Multi-timeframe alignment (M1, M5, H1, H4).
2. **Momentum**: MACD Histogram + ADX Strength confirmation.
3. **Structure**: SMC Order Blocks, FVG, and Inducement validation.
4. **Volatility**: ATR-based regime filtering (Trending vs. Ranging).

Final entry requires a **Trigger Candle** (Engulfing/Pin Bar) confirmation on the LTF.

---

## 🛡️ 4. Risk Management (The 7-Layer Stack)
1. **L1: Infrastructure** - Heartbeat monitor and Latency tracking.
2. **L2: Global Risk** - Max Drawdown and Daily Loss limits.
3. **L3: Symbol Risk** - Spread Blowout and ATR-relative safety.
4. **L4: News Risk** - 30-min blackout windows for NFP/FOMC.
5. **L5: Position Lifecycle** - Partial TP @ 1R, Breakeven @ 1.5R, and dynamic ATR Trailing Stops.
6. **L6: Correlation** - Cross-symbol exposure vetoes.
7. **L7: Final Gate** - Mandatory "3 of 4" Confluence check.

---

## 🛡️ Zero-Tolerance Standard
AAT enforces a 100% Zero-Tolerance standard across all tiers. No stubs, no placeholders, no dummy code. Every module is functional, connected, and audited for Defensive Alpha.

---
**Built with 💻 and ☕ by Jules (God Mode)**
*Capital preservation is the only Holy Grail.*
