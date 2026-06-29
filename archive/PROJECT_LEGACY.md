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
The system is built as a microkernel with event-driven decoupling, utilizing a **Multi-Brain Bayesian Orchestrator** pinned to 23 logical CPU processes.

### 🧩 Components
- **Python Hive (Coordinator):** Global risk management and Bayesian evidence aggregation.
- **Specialized Brains:** 23 isolated processes (Market Data, Trend, Liquidity, Momentum, Regime, Portfolio, etc.).
- **Analyst Tier:** Vectorized SMC, VSA, Technical Indicator, and Volatility engines.
- **MQL5 Agents:** Slim execution units with Sequence-Hardened protocol and Heartbeat failsafes.
- **Institutional Core:** Rust-based parallel VaR and high-speed logic gates.
- **Persistence:** SQLite (Audit Ledger) and Manager-backed IPC.

---

## 🧠 3. Quantitative Strategy (Confluence Engine)
AAT V3.0 enforces a **3-of-4 Confluence Rule**:
1. **Trend**: Multi-timeframe alignment (M1, M5, H1, H4).
2. **Momentum**: MACD Histogram + ADX Strength confirmation.
3. **Structure**: SMC Order Blocks, FVG, and Inducement validation.
4. **Volatility**: Realized Volatility-aware regime filtering.

Final entry requires a **Trigger Candle** (Engulfing/Pin Bar) confirmation on the LTF and dynamic RSI overextension checks.

---

## 🛡️ 4. Risk Management (The Institutional Stack)
1. **L1: Protocol Security** - Monotonic sequence numbering to detect packet loss.
2. **L2: Aggregated Risk** - Portfolio-wide Value-at-Risk (VaR) via Rust kernel.
3. **L3: Global Risk** - Max Drawdown and Daily Loss limits.
4. **L4: Symbol Risk** - Spread Blowout and ATR-relative safety.
5. **L5: News Risk** - 30-min blackout windows for NFP/FOMC.
6. **L6: Position Lifecycle** - Partial TP @ 1R, Breakeven @ 1.5R, and Hybrid ATR-SMC Trailing Stops.
7. **L7: Final Gate** - Bayesian Confidence Threshold (> 70%).

---

## 🛡️ Zero-Tolerance Standard
AAT enforces a 100% Zero-Tolerance standard across all tiers. No stubs, no placeholders, no dummy code. Every module is functional, connected, and audited for Defensive Alpha.

---
**Built with 💻 and ☕ by Jules (God Mode)**
*Capital preservation is the only Holy Grail.*
