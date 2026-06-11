# 🛠️ Project Phoenix: Engineering TODO (V7.1 Hybrid Revamp)

> **Status:** Phase 1 Refactoring
> **Focus:** Rust Kernel Integration & Toxicity Engine

## 🎯 Quarter 1: The Kernel Rewrite (Foundational)
- [ ] Initialize Rust project workspace (`phoenix-core`, `phoenix-bridge`).
- [ ] Implement **Lock-Free Event Bus** (`RingBuffer`) in Rust.
- [ ] Upgrade Security Layer to **AES-256-GCM** in Rust.
- [ ] Build **PyO3 Bridge** for Python-Rust event passing.

## ⚙️ Quarter 2: Abstraction & Persistence
- [ ] Define Rust Trait `BrokerAdapter` and implement `MT5Adapter` wrapper.
- [ ] Migrate Audit logs from SQLite to **PostgreSQL ACID**.
- [ ] Implement **Redis Cluster** for Hot State caching.
- [ ] Build the **Slow Loop** Context Engine (1s interval) in Python.

## 🚀 Quarter 3: The Fast Loop & Toxicity
- [ ] Implement **VPIN (Volume-Synchronized PIN)** in Rust.
- [ ] Build the **Fast Loop** Execution Engine (<100µs latency).
- [ ] Embed **ONNX Runtime C-API** in Rust for zero-copy AI inference.
- [ ] Standardize internal message passing via **Protobuf/gRPC**.

## 🛡️ Quarter 4: Resilience & Visualization
- [ ] Build `ChaosMonkey` service for automated failure injection.
- [ ] Launch **FinCon Terminal V2** (Next.js/WebSockets to Rust Core).
- [ ] Automate **L99 Certification** (CSCV/Deflated Sharpe calculation).
- [ ] Finalize Docker/K8s sovereign deployment scripts.

---
**Success Metric:** Internal Tick-to-Order Latency < 100µs.
