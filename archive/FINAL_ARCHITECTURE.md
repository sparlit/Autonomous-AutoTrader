# 🏆 FINALIZED ARCHITECTURE: AAT V2.3.0-ASCENDANT
**Architect**: Jules (God Mode)
**Status**: APPROVED & REINFORCED

## 1. The Phoenix Ascendant Hybrid Paradigm
AAT V2.3 utilizes a high-performance hybrid kernel where computationally expensive tasks are delegated to Rust, while complex orchestration and ML analysis remain in Python.

### 🧠 Stage 1: The Fast-Path (Sequential Brain)
- **Use Case**: High-priority scalping, emergency exits, and hard vetos.
- **Logic**: Linear scan of strategies S01-S05. First match triggers immediate action.
- **Hardware**: Runs on a dedicated "Fast-Brain" process with minimal latency.

### 🗳️ Stage 2: The Consensus-Path (Weighted Brain)
- **Use Case**: Standard entries, trend confirmation, regime changes.
- **Logic**: Parallel execution of strategies S06-S20. Sum of weighted signals >= 0.7 triggers a trade.
- **Hardware**: Distributed across "Worker-Brains" using `ProcessPoolExecutor` to maximize multi-core CPU utilization (i3/i5/i7).

### 🛡️ Stage 3: The Risk Arbiter & Rust Kernels
- **aat_heavy**: Rust-powered TCP ingestion and high-concurrency consensus management.
- **aat_rust_core**: Precision financial math using `rust_decimal` for lot sizing and risk offsets.
- **aat_rust**: Logical gatekeeper enforcing safety invariants and 7-layer risk validation.

## 2. Distributed Coordinator/Agent Model
- **Python Coordinator**: The central "Hive Mind" managing multi-symbol state, global risk limits, and the SYNC protocol.
- **Python Worker Brains**: Independent processes for parallelized strategy computation (SMC, VSA, Price Action).
- **MQL5 Slim Agents**:
  - `AAT_DataCollector`: Low-overhead sensor pushing real-time tick and MTF bar data.
  - `AAT_MasterExecutor`: Dedicated actuator for order execution using `OrderSendAsync`.
- **Triple-Dashboard Hub**:
  - **Native**: Dear PyGui for desktop-grade telemetry.
  - **Web**: FastAPI/WebSocket for remote monitoring.
  - **Terminal**: MT5 CCanvas for localized chart overlays.

## 3. Data Integrity & Persistence
- **Primary**: High-performance in-memory cache for active trade state and peak equity.
- **Secondary**: `aiosqlite` for local persistence of the Audit Trail and Trade Ledger.
- **Institutional Database**: `audit_records.db` for storing validated trading methods and strategy performance metadata.

## 4. Final Directory Structure
```text
/
├── config/             # symbol_maps, strategy_weights, global_risk, news_schedule
├── src/
│   ├── mql5/
│   │   ├── Experts/    # AAT_DataCollector, AAT_MasterExecutor, AAT_GlobalDashboard
│   │   └── Include/    # Bridge, Protocol, Dashboard, NativeSockets
│   ├── python/
│   │   ├── hive/       # Coordinator logic, Configuration
│   │   ├── brains/     # Sequential & Consensus engines, Strategies, Worker Pool
│   │   ├── analyst/    # Price Action, VSA, Volatility, Indicators
│   │   ├── bridge/     # Async TCP Server, Watchdog, MCP Server
│   │   └── execution/  # Trade Ledger, Position Manager, Risk Manager
│   └── rust_core/      # Rust native modules (aat_heavy, aat_rust_core)
├── tests/              # Unit, Integration, and Hardened Logic tests
└── audit_records.db    # Persistent SQLite findings and trade logs
```

## 5. Zero-Tolerance & Safety Compliance
- **Zero-Stub Standard**: 100% functional code. No stubs, placeholders, or "TODO" comments in production paths.
- **Failsafe BE**: Native MQL5 implementation moves stop-loss to breakeven if the Python heartbeat is lost.
- **SYNC Handshake**: Mandatory reconciliation of open MT5 tickets with the Python ledger upon every reconnection.

**Built with 💻 and ☕ by Jules (God Mode)**
*This architecture is the bedrock of Defensive Alpha.*
