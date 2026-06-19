# 🌌 Autonomous AutoTrader (AAT) - Forex Master Pro Edition

Welcome to the definitive institutional-grade autonomous trading system for MetaTrader 5. Engineered for **Defensive Alpha**, AAT prioritizes capital preservation through rigorous Smart Money Concepts (SMC), Volume-Spread Analysis (VSA), and multi-brain consensus logic.

---

## 📖 Table of Contents
1. [🌟 Overview & Philosophy](#-overview--philosophy)
2. [🚀 Core Features](#-core-features)
3. [🏗️ Technical Architecture](#️-technical-architecture)
4. [🛠️ Installation & Setup](#️-installation--setup)
5. [📈 How to Use](#-how-to-use)
6. [🛡️ Risk Management (Institutional)](#️-risk-management-institutional)
7. [🗺️ Strategic Roadmap](#️-strategic-roadmap)
8. [📚 Wiki & Technical Deep-Dive](#-wiki--technical-deep-dive)

---

## 🌟 Overview & Philosophy
The AAT system is built on the principle that **profit is a byproduct of discipline and risk management**. Unlike retail bots that chase indicators, AAT operates as a **Specialized Agency Model**:
- **Sensor (MT5 DataCollector)**: Ingests raw market reality.
- **Brain (Python Coordinator)**: Processes data through a multi-threaded consensus engine.
- **Actuator (MT5 MasterExecutor)**: Executes institutional orders with millisecond precision.

---

## 🚀 Core Features
- **SMC Alpha Engine**: Algorithmic detection of Order Blocks, Change of Character (CHoCH), Fair Value Gaps (FVG), and high-probability Liquidity Sweeps.
- **VSA Verification**: Uses "Effort vs Result" logic to confirm institutional momentum and filter retail fakeouts.
- **Multi-Timeframe (MTF) Alignment**: Every M1/M5 entry is verified against H1 and H4 macro trends.
- **Latency-Agnostic Execution**: Uses point-based SL/TP offsets to ensure risk accuracy regardless of network jitter.
- **Autonomous Lifecycle**: Automated partial take-profits (50% at 1R), move-to-breakeven, and ATR-based trailing stops.
- **Failsafe System**: Native MQL5 heartbeat monitor that moves trades to safety if the Python connection is lost.

---

## 🏗️ Technical Architecture
### 1. The Multi-Brain Pipeline
Strategies are processed in parallel using a `ProcessPoolExecutor` to bypass the Python GIL:
- **HTF Brain**: Analyzes macro bias and major supply/demand zones.
- **LTF Trigger Brain**: Identifies Pin Bars and Engulfing candles for precision entry.
- **Consensus Engine**: Requires 3 of 4 filters (Trend, Momentum, Structure, Volatility) to align.
- **Correlation Brain**: Manages net currency group exposure (e.g., max 2x USD exposure).

### 2. The Fault-Tolerant Bridge
- **Async TCP**: High-performance local IPC with robust internal buffering.
- **Minified Protocol**: Uses short-key JSON (e.g., 's' for symbol, 't' for type) to minimize bandwidth.
- **Persistent Ledger**: aiosqlite-based trade tracking ensures no desync between MT5 and Python.

---

## 🛠️ Installation & Setup

### Phase 1: Python Environment
1. **Requirements**: Python 3.10+
2. **Install Dependencies**:
   ```bash
   pip install pandas numpy pydantic ujson aiosqlite pytest-asyncio
   ```
3. **Run the Brain**:
   ```bash
   python src/python/hive/coordinator.py
   ```

### Phase 2: MetaTrader 5 Setup
1. **DataCollector**: Attach `src/mql5/Experts/AAT_DataCollector.mq5` to any chart.
2. **MasterExecutor**: Attach `src/mql5/Experts/AAT_MasterExecutor.mq5` to a single dedicated chart.
3. **Configuration**: Ensure "Allow DLL imports" and "Allow Algo Trading" are checked.

---

## 🛡️ Risk Management (Institutional)
AAT is designed to satisfy professional prop-firm requirements:
- **1% Precise Risk**: Calculated using real-time `TICK_VALUE` for perfect exposure.
- **Relative Drawdown Protection**: Tracks **Equity Peaks** in SQLite to prevent breaching drawdown limits.
- **Revenge Trading Guardrail**: Mandatory 4-hour cooldown for any symbol that hits Stop Loss.
- **News 'Kill-Zone'**: Automated 30-minute no-trade window around high-impact events (NFP/FOMC).

---

## 🗺️ Strategic Roadmap
### ✅ Phase 1: MVP (Completed)
- Multi-brain architecture, SMC logic, MTF Data Feed, and persistent ledger.
### 📍 Phase 2: Scaling (Current)
- Optimization of VSA logic and expansion to Multi-Symbol Dashboard.
### 🚀 Phase 3: Institutional
- FIX Protocol Gateway and advanced Monte Carlo pre-trade simulations.

---

## 📚 Wiki & Technical Deep-Dive

### 1. SMC Detection Logic (`price_action.py`)
Order Blocks are only valid if the impulsive move is **> 1.5x ATR**. Pivot detection requires a **5-bar confirmation** to eliminate repaint risk.

### 2. SYNC Handshake (`coordinator.py`)
Upon reconnection, the EA sends its current open tickets. Python reconciles these against the database. If a trade was closed while the server was down, the ledger is updated, and a cooldown is triggered if it was an SL hit.

### 3. Failsafe Mode (`AAT_BridgeClient.mqh`)
If the Python heartbeat is missing for > 60 seconds, the EA:
1. Stops accepting new signals.
2. Moves all profitable trades to Entry + 10 points.
3. Logs a critical system alert.

### 4. VSA Effort vs Result (`volatility.py`)
- **Effort**: Relative Volume vs 20-period average.
- **Result**: Candle spread vs 20-period average.
- **Absorption**: High Effort (Volume) + Low Result (Spread) = Signal rejection.

---

**Built with 💻 and ☕ by Jules (God Mode)**
*This project is 100% FOSS. Trade responsibly.*
