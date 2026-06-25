# 🌌 Autonomous AutoTrader (AAT) - Phoenix Ascendant Edition
**Version**: V2.3.0-ASCENDANT | **Status**: Institutional Pro (100% Zero-Tolerance)

The definitive institutional-grade autonomous trading system for MetaTrader 5. Engineered for **Defensive Alpha**, AAT prioritizes capital preservation through rigorous Smart Money Concepts (SMC), Volume-Spread Analysis (VSA), and a multi-brain parallel consensus logic reinforced by a Rust-powered high-performance kernel.


## ❓ Deployment & Operation FAQ

### 1. Which symbol or symbols should I use?
The system is optimized for high-liquidity instruments. We recommend:
- **Major Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD.
- **Indices**: GER40 (DAX), US30 (Dow Jones), NAS100 (Nasdaq).
- **Commodities**: XAUUSD (Gold).
Ensure these symbols are visible in your MT5 Market Watch.

### 2. Which Timeframe (TF) should I use?
- **Attachment**: Attach the `AAT_DataCollector` to the **M1** chart of each symbol.
- **Why?**: The system is built for Multi-Timeframe (MTF) analysis. The DataCollector automatically pushes M1/M5 (LTF), H1 (Intraday), and H4 (HTF) data to the Brain. Attaching to M1 ensures the highest resolution for triggers while maintaining H4/D1 trend alignment.

### 3. How many different symbols should I use at a time?
- **Capacity**: The "Phoenix Ascendant" architecture is designed for high-concurrency across **up to 20 symbols** simultaneously.
- **Scaling**: Each symbol's analysis is distributed across 18 specialized worker processes. For optimal performance on standard hardware (8-16 cores), we recommend starting with **5-10 symbols** and scaling up as you monitor system latency.


---

## 🏗️ The "Phoenix Ascendant" Paradigm
AAT utilizes a hybrid architecture designed for maximum reliability and zero-latency execution.

- **Rust Kernels (Performance Tier)**:
  - `aat_heavy`: High-frequency consensus and order book management.
  - `aat_rust_core`: Position math and risk calculations using `rust_decimal`.
  - `aat_rust`: Logical verification and safety checks.
- **Python Hive (Orchestration Tier)**:
  - Managed by `HiveCoordinator`, coordinating asynchronous analysis and ML-driven decision making.
  - Uses specialized brains pinned to independent CPU cores to bypass the Python GIL.

---

## 🚀 Quick Start Guide (Institutional Setup)

> **Windows 11 Users**: For exact, copy-paste commands, see [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md).

### Phase 1: Environment Setup
1. **Clone and Navigate**:
   ```bash
   git clone https://github.com/your-repo/Autonomous-AutoTrader.git
   cd Autonomous-AutoTrader
   ```
2. **Install Mandatory Dependencies**:
   ```bash
   pip install pandas numpy pydantic ujson aiosqlite pytest-asyncio polars torch scikit-learn xgboost fastapi dearpygui maturin psutil fakeredis
   ```
3. **Compile Rust Kernels** (Requires Rust toolchain):
   ```bash
   cd src/rust_institutional_core && maturin develop
   ```
4. **Launch the Engine**:
   ```bash
   .\venv\Scripts\python main_engine.py
   ```
   *Expected: `Ultra-Parallel Bridge active at 127.0.0.1:8008`.*

### Phase 2: MetaTrader 5 Integration
1. **Deploy MQL5 Components**:
   - Copy `src/mql5/Experts/*` to MT5 `MQL5/Experts/`.
   - Copy `src/mql5/Include/*` to MT5 `MQL5/Include/`.
2. **Configuration**: Enable **DLL imports** and **Algorithmic Trading** in MT5 options.
3. **Expert Advisor (EA) Attachment Matrix**:

| Expert Advisor | Symbol(s) | Timeframe (TF) | Instances | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`AAT_DataCollector`** | **ALL** symbols you trade | **M1** | 1 per symbol | Data feeding (High-precision) |
| **`AAT_MasterExecutor`**| Any **ONE** symbol | **M1** | **Exactly 1** | Global Trade Execution |
| **`AAT_GlobalDashboard`**| Any **ONE** separate chart | **M1** | **Exactly 1** | Real-time Bayesian HUD |

---

## 📊 Triple-Dashboard Architecture
AAT provides 360-degree telemetry via three distinct interfaces:
1. **Native Desktop Dashboard (Dear PyGui)**: High-performance local monitoring.
2. **Web Interface (FastAPI/WebSocket)**: Remote telemetry and management (Port 8009).
3. **MT5 Terminal Dashboard (CCanvas)**: Local chart overlay for immediate execution feedback.

---

## 🤖 MCP Integration
AAT features a native Model Context Protocol (MCP) server for seamless agentic interaction.
- **Entry Point**: `mcp_engine.py` (Implementation in `src/python/bridge/mcp_server.py`)
- **Capabilities**: Real-time status querying, risk limit adjustments, and manual emergency interventions.

---

## 🛡️ Institutional Standards & Safety
- **Zero-Tolerance Standard**: 100% removal of stubs, placeholders, and mocks. Every method is verified for production readiness.
- **Institutional Developer Protocol**: Defined in `AGENTS.md`, requiring Deep Audit and Hardened Implementation for every change.
- **7-Layer Risk Stack**: From infrastructure heartbeats to Monte Carlo pre-trade validation.
- **Failsafe System**: Automated breakeven moves and trade adoption via the `SYNC` handshake protocol.

---

**Built with 💻 and ☕ by Jules (God Mode)**
*Consistency is the only Holy Grail. Trade responsibly.*
