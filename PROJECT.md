# 🪐 Project Phoenix: Sovereign Execution Engine (V1.32)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.32 (Edge Persistence Integration)
**Focus:** Rust-Python Polyglot Microkernel & MQL5 Edge Data Integrity.

✅ **Production Core Refactoring:** (Hybrid Kernel Init)
✅ **MQL5 Local Persistence:** (SQLite Partitioned Module COMPLETE)
✅ **Governance Layer V2:** (Pre-Computed Context)
✅ **Universal Broker Abstraction Layer:** (Active)
✅ **Order Flow Toxicity Engine:** (VPIN Integration)

🔄 **Multi-Asset Autonomy:** (FX, Metals, Crypto, Indices)
🔄 **Recursive Refinement:** (100-Cycle Protocol Implementation)

⚠️ **CRITICAL NOTE:** V1.32 formalizes the **MQL5 Edge Persistence Layer**. We have implemented a persistent, partitioned SQLite architecture to ensure that every trade, tick, and log event at the broker edge is captured with ACID integrity before synchronization with the PostgreSQL institutional store.

✅ **Core Integrity:** Hybrid Kernel (Rust Nervous System + Python Brain).
✅ **Governance:** PostgreSQL (Institutional) + SQLite (Edge Local).
✅ **Standard:** L99-Standard V3 / Edge-Integrity Certified.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (Active).

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🏗️ Architecture: The Hybrid Kernel (Rust-Python)
The engine utilizes a polyglot microkernel for extreme performance and safety.

### 🗃️ 4.2 MQL5 Edge Persistence (SQLite Core)
The terminal-side persistence layer ensures local data sovereignty and recovery:
- **Monthly Table Partitioning:** Automated generation of `trades_YYYYMM`, `market_data_YYYYMM`, and `system_logs_YYYYMM` to prevent large-file performance degradation.
- **Performance Standard:** **WAL (Write-Ahead Logging)** mode enabled for optimal concurrent access during high-frequency trading.
- **Automated Maintenance:** Mandatory daily/monthly routines:
  - `Vacuum()`: Reclaims unused disk space.
  - `IntegrityCheck()`: Verifies database structure.
  - `Backup()`: Creates snapshots of the current month's data.
  - `DropOldMonthlyTables()`: Enforces a 24-month retention policy.

#### Edge Table Schemas:
- **Trades:** Ticket, action, lot volume (units/100.0), SL/TP, profit/swap/commission, slippage, and duration.
- **Market Data:** OHLCV, spread, and indicators per timeframe.
- **System Logs:** Module-specific diagnostics (INFO/WARN/ERROR) with terminal ID.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Order Flow Toxicity Framework
We operate on **Toxicity Detection** rather than liquidity prediction.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Execution Standards (V1.32)
- **Volume Normalization:** All deal volumes are normalized to standard lots (division by 100.0) at the persistence point.
- **Position Tracking:** Accurate SL/TP detection via stateful comparison of position snapshots stored in the local SQLite audit trail.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V7.1)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: The Hybrid Kernel (Current)
- [x] **Implement Persistent SQLite Database for MQL5 (Partitioned).**
- [ ] Port Event Bus to Rust (Lock-free Ring Buffer).
- [ ] Create PyO3 Bindings for Python logic.
- [ ] Abstract MT5 commands to Universal Broker traits.

---

## 📜 17. Appendices & Data Dictionary
*Capital preservation is the primary outcome of discipline.*
