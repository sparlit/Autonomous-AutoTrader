# 🏆 Institutional Guide: Real-Time Telemetry & Advanced Risk (V3.3.0)

AAT V3.3.0-ASCENDANT introduces high-fidelity trade tracking and Bayesian-weighted institutional position sizing. This guide explains how to utilize these new features for optimal capital allocation.

---

## 📊 1. Real-Time Trade Tracking

The system now provides tick-by-tick monitoring of all open positions across three distinct layers.

### A. Dashboard Metrics
For every active trade, the following metrics are now calculated in real-time:
- **PL ($)**: Floating Profit or Loss in your account currency.
- **PL (PTS)**: Floating Profit or Loss in raw points (pips).
- **Duration**: The exact age of the trade (Minutes/Seconds).
- **Status**: Current management state (e.g., `OPEN`, `PARTIAL_HIT`, `BE_PROTECTED`).

### B. Accessing the Dashboards
1. **Native HUD**: The Dear PyGui window now features a dedicated **ACTIVE INSTITUTIONAL POSITIONS** table below the brain health metrics.
2. **Web Terminal**: Accessible via `http://localhost:8009`, featuring a responsive "Live Institutional Trades" panel that updates via WebSocket.

---

## 🛡️ 2. Institutional Risk Engine

V3.3.0 moves beyond simple ATR-based sizing. It implements a **Bayesian-Weighted Alpha Multiplier** for every trade.

### A. The Sizing Formula
The `RiskManager` now utilizes `calculate_institutional_params`, which adjusts position size based on:
1. **Bayesian Probability**: Signals with higher posterior probability receive larger allocations.
2. **Signal Confluence**: The "3 of 4" rule (Trend, Momentum, Structure, Volatility) scales the trade. 4/4 agreement triggers maximum institutional weight.
3. **Market Regime**: Fast-trending markets receive a 1.2x multiplier, while choppy regimes are throttled to 0.5x.

### B. Dynamic SL/TP Calibration
- **Stop Loss**: Remains ATR-relative for institutional protection.
- **Take Profit**: High-confidence signals (Probability > 70%) receive a dynamic TP extension, allowing winners to run further based on Bayesian conviction.

---

## 🛠️ 3. How-To: Reading the Signals

| Metric | Level | Action |
|--------|-------|--------|
| **Probability** | > 85% | Institutional Core Maximum Allocation. |
| **Confluence** | 4/4 | High conviction; TP target automatically extended. |
| **PL (PTS)** | > 50 | Partial TP likely triggered; SL moved to Breakeven. |
| **Status** | `PARTIAL_HIT` | Trade is risk-free (BE); remaining 50% is trailing. |

---

## 🚀 4. Deployment Instructions

1. **Initialize the Hive**: `python aat.py run`.
2. **Open the Web Terminal**: Navigate to `http://localhost:8009`.
3. **Verify Connection**: Ensure `ACTIVE INSTITUTIONAL POSITIONS` appears in the Native HUD.
4. **Monitor Alpha**: Observe how the system scales position sizes dynamically as MetaBrain confluence shifts.

**Built with 💻 and ☕ by Jules (God Mode)**
*Consistency is the only Holy Grail. Trade responsibly.*
