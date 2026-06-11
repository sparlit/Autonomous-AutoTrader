# 🛠️ Project Phoenix: Engineering TODO (V7.1 Revamp)

> **Status:** Critical Path Engineering
> **Focus:** Hybrid Kernel Implementation & Rust Integration

## 🎯 Quarter 1: The Kernel Rewrite (Foundational)
- [ ] Initialize Rust project workspace (`phoenix-core`, `phoenix-bridge`).
- [ ] Set up `Cargo.toml` with dependencies: `tokio`, `pyo3`, `ring`, `crossbeam`.
- [ ] Design and implement **Lock-Free Event Bus** (`RingBuffer`) in Rust.
- [ ] Implement **AES-256-GCM** encryption module in Rust.
- [ ] Create Python-Rust bridge using `maturin` and PyO3.
- [ ] Implement data serialization using Cap'n Proto or MsgPack.

## ⚙️ Quarter 2: The Abstraction & Persistence
- [ ] Define Rust Trait `BrokerAdapter` and implement `MT5Adapter`.
- [ ] Set up **PostgreSQL** (Relational) and **Redis Cluster** (Hot State).
- [ ] Write DB Abstraction Layer in Rust for async persistence.
- [ ] Build Python Asyncio `ContextManager` for the **Slow Loop** (Regimes, Macro).
- [ ] Remove SQLite dependency from production build.

## 🚀 Quarter 3: The "Fast Loop" & Toxicity
- [ ] Implement **Order Flow Toxicity** (VPIN, Imbalance Ratio) in Rust.
- [ ] Build the **Fast Loop** Execution Engine in Rust (<100µs).
- [ ] Integrate **ONNX Runtime** C-API in Rust for zero-copy AI inference.
- [ ] Implement thread-safe Atomic counters for position sizing.

## 🛡️ Quarter 4: Resilience & UI
- [ ] Build `ChaosMonkey` service for process kills and latency injection.
- [ ] Launch **FinCon Terminal V2** (Next.js/WebSockets).
- [ ] Automate L99 Certification (CSCV/Deflated Sharpe scripts).
- [ ] Dockerize the entire stack for one-click deployment.

## 📝 Engineering Debt & Cleanup
- [ ] Deprecate legacy `src/shared/utils/bus.py`.
- [ ] Replace `print()` with `tracing` (Rust) and `structlog` (Python).
- [ ] Standardize Error Handling with `anyhow` (Rust).
