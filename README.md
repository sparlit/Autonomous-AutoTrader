# 🌌 Autonomous AutoTrader (AAT) - Phoenix Ascendant Edition
**Version**: V2.3.0-ASCENDANT | **Status**: Institutional Pro (100% Zero-Tolerance)

The definitive institutional-grade autonomous trading system for MetaTrader 5. Engineered for **Defensive Alpha**, AAT prioritizes capital preservation through rigorous Smart Money Concepts (SMC), Volume-Spread Analysis (VSA), and a multi-brain parallel consensus logic reinforced by a Rust-powered high-performance kernel.

---

## 🏗️ The "Phoenix Ascendant" Paradigm
AAT utilizes a hybrid architecture designed for maximum reliability and zero-latency execution.

- **Rust Kernels (Performance Tier)**:
  - `aat_heavy`: High-frequency consensus and order book management.
  - `aat_rust_core`: Position math and risk calculations using `rust_decimal`.
  - `aat_rust`: Logical verification and safety checks.
- **Python Hive (Orchestration Tier)**:
  - Managed by `HiveCoordinator`, coordinating asynchronous analysis and ML-driven decision making.
  - Uses `ProcessPoolExecutor` to bypass the Python GIL, ensuring multi-core strategy analysis.

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
   pip install pandas numpy pydantic ujson aiosqlite pytest-asyncio polars torch scikit-learn xgboost fastapi dearpygui maturin
   ```
3. **Compile Rust Kernels** (Requires Rust toolchain):
   ```bash
   cd src/rust_institutional_core && maturin develop
   # Repeat for rust_heavy and rust_brain (if present)
   ```
4. **Launch the Engine**:
   ```bash
   ..\venv\Scripts\python main_engine.py
   ```
   *Expected: `Ultra-Parallel Bridge active at 127.0.0.1:5555`.*

### Phase 2: MetaTrader 5 Integration
1. **Deploy MQL5 Components**:
   - Copy `src/mql5/Experts/*` to MT5 `MQL5/Experts/`.
   - Copy `src/mql5/Include/*` to MT5 `MQL5/Include/`.
2. **Configuration**: Enable **DLL imports** and **Algorithmic Trading** in MT5 options.
3. **Attach Agents**:
   - `AAT_DataCollector`: Attach to every symbol chart.
   - `AAT_MasterExecutor`: Attach to **only one** chart for order execution.
   - `AAT_GlobalDashboard`: Attach to a dedicated monitor chart.

---

## 📊 Triple-Dashboard Architecture
AAT provides 360-degree telemetry via three distinct interfaces:
1. **Native Desktop Dashboard (Dear PyGui)**: High-performance local monitoring.
2. **Web Interface (FastAPI/WebSocket)**: Remote telemetry and management.
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

## 📉 Performance & Strategy
- **SMC Alpha Core**: Liquidity Sweeps, Order Blocks (>1.5x ATR), and CHoCH detection.
- **VSA Verification**: "Effort vs Result" anomaly detection for signal conviction.
- **Parallel Strategy Pipeline**:
  - **Fast-Path**: Linear scan for emergency exits and scalping.
  - **Consensus-Path**: Parallel weighted voting (|score| >= 0.7) for standard entries.

---

**Built with 💻 and ☕ by Jules (God Mode)**
*Consistency is the only Holy Grail. Trade responsibly.*
