# 🪐 Project Phoenix: Sovereign Execution Engine (V1.31)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.31 (Hybrid Revamp Integration)
**Focus:** Rust-Python Polyglot Microkernel & Adverse Selection Protection.

✅ **Production Core Refactoring:** (Hybrid Kernel Init)
✅ **Governance Layer V2:** (Pre-Computed Context)
✅ **Universal Broker Abstraction Layer:** (Active)
✅ **Order Flow Toxicity Engine:** (VPIN Integration)

🔄 **Multi-Asset Autonomy:** (FX, Metals, Crypto, Indices)
🔄 **Recursive Refinement:** (100-Cycle Protocol Implementation)

⚠️ **CRITICAL NOTE:** V1.31 integrates the **Hybrid Revamp (V7.1.0)** specifications. We have moved from a pure Python stack to a **Rust-Python Hybrid Kernel** to eliminate GIL bottlenecks and achieve deterministic sub-100µs internal latency.

✅ **Core Integrity:** Hybrid Kernel (Rust Nervous System + Python Brain).
✅ **Governance:** PostgreSQL (Audit) + Redis (SPMC Bus) + QuestDB (Telemetry).
✅ **Standard:** L99-Standard V3 / Hybrid-Institutional Certified.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (Active).

### 🔥 The Autopsy (Ruthless Devil's Advocate Integration)
The project has undergone a ruthless autopsy identifying the following existential failure points:
1.  **The "Sub-millisecond" Python Lie:** Python GIL and GC pauses make consistent sub-ms latency impossible; move execution to Rust.
2.  **The "Sovereign" Fallacy:** Tight coupling to MT5 is a captive state, not sovereignty; implement Universal Broker API.
3.  **The "Risk of Ruin" Paradox:** Strict <5% DD targets risk paralysis; move to "Regime-Adjusted Expectancy."
4.  **SQLite Audit Bottleneck:** SQLite writes block high-frequency buses; move to PostgreSQL and Redis Ring Buffers.
5.  **Liquidity Hallucination:** Retail tick data is broker-queue data, not market liquidity; move to Order Flow Toxicity (VPIN).
6.  **Decision Latency Trap:** Sequential 8-stage checks are too slow; implement Pre-Computed Governance (Slow/Fast Loops).
7.  **Security Legacy:** AES-256-CBC is vulnerable; immediately upgrade to AES-256-GCM.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** To architect the world's first **Hybrid High-Frequency Retail Platform**, combining the ease of Python for research with the raw speed of Rust for execution.

**Mission:** To maximize risk-adjusted expectancy through **Deterministic Latency** and **Adverse Selection Protection**. We react to the present with institutional speed.

### 📊 Performance Mandates (Dynamic & Regime-Adjusted)
| Metric | Condition | Target | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | Low Volatility Regime | > 2.5 | High |
| **Sharpe Ratio** | High Volatility/Crisis | > 1.5 | High |
| **Sortino Ratio** | Global | > 3.0 | High |
| **MAR Ratio** | Global | > 2.0 | High |
| **Execution Latency** | Tick-to-Order (Internal) | < 100µs | **CRITICAL** |
| **Capital Preservation** | Absolute | Primary | **CORE** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Values (V7.1 Hybrid Realignment)
- **Sovereignty:** Broker-Agnostic Execution. Your logic, your capital, your choice of counterparty.
- **Determinism:** No Garbage Collection pauses. No blocking I/O. Predictable execution paths.
- **Transparency:** Provenance logging for every nanosecond of decision making.
- **Institutional Discipline:** We refuse to trade in toxic liquidity conditions.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🏗️ Architecture: The Hybrid Kernel (Rust-Python)
The engine utilizes a polyglot microkernel for extreme performance and safety:
- **Sovereign Ingress (Rust):** High-speed TCP/TLS Gateway (AES-256-GCM).
- **The Event Bus (Rust):** Lock-free, single-producer multi-consumer (SPMC) ring buffer.
- **The Compute Engine (Python):** Asyncio workers for AI inference and Strategy logic via PyO3 bindings.
- **The Execution Layer (Rust):** Direct interface to the Universal Broker Adapter (MT5/cTrader/FIX).

### 🏗️ Dual-Loop Decision Framework
- **Slow Loop (Context, 1s):** Regime ID, Macro Assessment, Portfolio Exposure. *Output:* Trading Permission Ticket.
- **Fast Loop (Execution, <100µs):** Toxicity Check (VPIN), Risk Check, Order Dispatch.

### 🧱 Technical Specifications (V7.1)
- **Core Kernel:** Rust 1.70+ (Tokio Async Runtime).
- **Security:** AES-256-GCM + SHA-384 HMAC.
- **Inference:** ONNX Runtime (C++ bindings) for zero-copy execution.
- **Protocol:** gRPC/Protobuf for internal communication.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Order Flow Toxicity Framework
We operate on **Toxicity Detection** rather than liquidity prediction:
- **VPIN:** Volume-Synchronized Probability of Informed Trading.
- **Imbalance Ratio:** Real-time bid/ask divergence.
- **Jitter Detection:** Broker-side quote stuffing or latency arbitrage monitoring.

### 🧠 Machine Learning Architecture V3
- **Models:** XGBoost/LightGBM (Python training -> ONNX export -> Rust execution).
- **Online Learning:** River (Python) for Adaptive Trees on tick streams.
- **Circuit Breakers:** Auto-disable model for 24h if price drops > 0.2% within 10s of Long signal.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V3 (Reactive)
- **Layer 1: Execution Risk:** Latency check (if order > 200ms, abort).
- **Layer 2: Symbol Risk:** Volatility shrink/expansion monitor.
- **Layer 3: Correlation:** Net exposure calc.
- **Layer 4: Drawdown Velocity:** If DD drops 2% in 1 min, Global Halt.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Universal Broker Abstraction
The system utilizes a **Universal Broker API** allowing for the "Ability to Leave":
- Supported Adapters: MT5, cTrader, FIX 4.4/5.0.
- All broker commands abstracted to generic traits.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V7.1)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: The Hybrid Kernel (Current)
- [ ] Port Event Bus to Rust (Lock-free Ring Buffer).
- [ ] Create PyO3 Bindings for Python logic.
- [ ] Abstract MT5 commands to Universal Broker traits.
- [ ] Migrate Encryption to AES-256-GCM in Rust.

### 🚀 Phase 2: Toxicity & Speed
- [ ] Implement VPIN/Toxicity Engine.
- [ ] Refactor Decision Engine for Slow/Fast Dual-Loop.
- [ ] Replace SQLite with Redis/PostgreSQL combo.

### 🌐 Phase 3: The FinCon Terminal & Scale
- [ ] Launch React/Next.js Terminal connecting to Rust Core.
- [ ] Implement Multi-Broker simultaneous deployment.

---

## 📜 12. Engineering TODO (V7.1 Blueprint)
*Quarterly milestones for the implementation of the Hybrid Kernel.*

- **Q1:** Rust Workspace setup, Lock-free Bus, AES-GCM, PyO3 Bridge.
- **Q2:** Universal Broker Traits, Postgres/Redis Migration, Slow Loop Context Engine.
- **Q3:** Rust VPIN/Toxicity calculation, Fast Loop Execution Engine, ONNX Integration.
- **Q4:** ChaosMonkey service, FinCon Terminal V2 WebSockets, L99 Automation.

---

## 📜 13. Sovereign Operational Rituals (V1.29 Expansion)
*Mandatory daily rituals to ensure the alignment of the human-machine sovereign ensemble.*

---

## 📜 17. Appendices & Data Dictionary
*Capital preservation is the primary outcome of discipline.*
