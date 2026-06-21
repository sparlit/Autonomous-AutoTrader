# 🌌 Project Autonomous AutoTrader (AAT)
**Internal Code-Name**: Phoenix Gauntlet / Phoenix Ascendant
**Version**: V2.3.0-ASCENDANT (Zero-Tolerance)

## 📖 1. Project Identity & Vision
AAT is a high-probability, autonomous trading system engineered for MetaTrader 5, powered by a hybrid "Phoenix Ascendant" kernel combining Rust's performance with Python's orchestration. It operates on the principle of **Defensive Alpha**: capital preservation is the primary objective; profit is a secondary outcome of discipline.

### 💎 Core Values (V2.3.0)
- **Zero-Tolerance Policy**: 100% removal of stubs, placeholders, and mocks. Only production-ready code is permitted.
- **Sovereignty**: 100% FOSS. Your data, your keys, your execution.
- **Institutional Rigor**: Every strategy and method must pass a 5-step audit before deployment.
- **Performance**: Multi-core parallelism and Rust-native risk checks for sub-millisecond safety validation.

---

## 🛠️ 2. System Overview
The system follows a distributed Coordinator/Agent model, decoupling high-frequency data ingestion from complex decision logic.

### 🧩 Components
- **Python Hive (Coordinator)**: Manages global risk, multi-symbol state, and asynchronous strategy analysis.
- **Rust Kernels**:
  - `aat_heavy`: High-concurrency engine for consensus and telemetry.
  - `aat_rust_core`: Financial math (pip values, lot sizing) using decimal-accurate Rust types.
  - `aat_rust`: Logical gatekeeper for safety-critical execution.
- **MQL5 Agents**:
  - `DataCollector`: Specialized sensor pushing MTF (M1-D1) data streams.
  - `MasterExecutor`: Slim actuator for order execution using `OrderSendAsync`.
  - `Dashboard`: High-frequency chart rendering via `CCanvas`.

---

## 🧠 3. Quantitative Strategy
AAT uses a multi-timeframe (MTF) approach, aligning H4/D1 institutional bias with M1/M5 entry triggers.

### 🛡️ Decision Engine
1. **Stage 1: Veto Filters**: Hard checks for news (Forex Factory), spread, and session activity.
2. **Stage 2: Fast-Path (Sequential)**: Immediate detection of scalping setups and emergency exits.
3. **Stage 3: Consensus-Path (Parallel)**: Weighted voting across SMC, VSA, and indicator-based brains.
4. **Stage 4: Risk Arbiter**: Final validation against the 7-Layer Risk Stack.

---

## 🏗️ 4. Technical Specifications
- **Architecture**: Microkernel (plug-in) with event-driven decoupling.
- **Parallelism**: `ProcessPoolExecutor` for strategy workers + `Tokio` (Rust) for TCP ingestion.
- **Persistence**: `aiosqlite` for local ledger + in-memory thread-safe cache for stats.
- **ML Stack**: XGBoost regime classification, Polars feature engineering, and PyTorch signal ranking.

---

## 🛡️ 5. Risk Management Stack
1. **L1: Infrastructure**: Heartbeat monitoring and SYNC protocol.
2. **L2: Global Risk**: Daily Loss, Absolute/Relative Drawdown (Peak Equity tracking).
3. **L3: Symbol Risk**: Group exposure limits and currency correlation matrix.
4. **L4: Execution Risk**: Latency-agnostic point-based SL/TP calculation.
5. **L5: Safety Protocol**: 4-hour cooldown after losses; automated BE on heartbeat loss.

---

## 👥 6. Institutional Developer Protocol
All development must adhere to the standard codified in `AGENTS.md`:
1. **Deep Audit**: Recursive analysis of files for stubs/flaws.
2. **Hardened Implementation**: Standard-compliant, side-effect-free code.
3. **Recursive Teardown**: Verification and cleanup of auxiliary branches.

---

## 📜 7. Appendices
- **Institutional Database**: `audit_records.db` stores all trading methods and strategy logs.
- **Version Control**: Single-branch (main) institutional standard.
- **Performance Config**: `OMP_NUM_THREADS` and `MKL_NUM_THREADS` optimized for multi-core parallelism.

**Built with 💻 and ☕ by Jules (God Mode)**
