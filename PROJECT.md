# 🪐 Project Phoenix: Sovereign Execution Engine (V1.12)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.12 (Hybrid Kernel Refactoring)
**Focus:** Rust-Python Hybrid Kernel & Order Flow Toxicity.

✅ **Production Core Refactoring (Hybrid Kernel Init)**
✅ **Governance Layer V2 (Pre-Computed Context)**
✅ **Universal Broker Abstraction Layer**
✅ **Order Flow Toxicity Engine Integration**

⚠️ **CRITICAL NOTE:** V1.12 represents a fundamental realignment around the **Hybrid Kernel**. We have moved from a pure Python stack to a Rust-Python polyglot architecture to eliminate GC pauses and achieve deterministic sub-100µs internal latency.

✅ **Core Integrity:** Rust-Python Hybrid / Modular Monolith.
✅ **Governance:** PostgreSQL (Relational) + Redis (Hot State) + QuestDB (Telemetry).
✅ **Standard:** L99-Standard V3 Certified Framework.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (In-Progress).

### 🧐 Institutional Reality Audit (V1.12 Refinement)
1.  **The Sub-millisecond Lie:** Python alone cannot guarantee deterministic latency. **Rust** now handles the "Nervous System" (Event Bus, Execution, Encryption).
2.  **The Sovereign Fallacy:** Sovereignty is the *ability to leave*. We have implemented a **Universal Broker API** to abstract away MT5/cTrader dependencies.
3.  **Liquidity vs Toxicity:** We replace "Liquidity Inference" (often noise) with **Order Flow Toxicity Detection** (VPIN) to detect adverse selection empirically.
4.  **Decision Latency:** The 8-stage process is split into a **Slow Loop** (Context) and a **Fast Loop** (Execution) to prevent analysis paralysis.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** To architect the world's first **Hybrid High-Frequency Retail Platform**, combining the ease of Python for research with the raw speed of Rust for execution.

**Mission:** To maximize risk-adjusted expectancy through **Deterministic Latency** and **Adverse Selection Protection**. We react to the present with institutional speed.

### 📊 Performance Mandates (Dynamic & Tiered)
| Metric | Condition | Target | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | Low Volatility Regime | > 2.5 | High |
| **Sharpe Ratio** | High Volatility/Crisis | > 1.5 | High |
| **Sortino Ratio** | Global | > 3.0 | High |
| **Max Drawdown** | Defensive Mode | < 5% | **ABSOLUTE** |
| **Max Drawdown** | Offensive Mode | < 12% | **ABSOLUTE** |
| **Risk of Ruin** | Annualized | < 0.5% | **ABSOLUTE** |
| **Internal Latency** | Tick-to-Order | < 100µs | **CRITICAL** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Values (V7.1 Hybrid Realignment)
- **Sovereignty:** Broker-Agnostic Execution. Your logic, your capital, your choice of counterparty.
- **Determinism:** No Garbage Collection pauses. No blocking I/O. Predictable execution paths.
- **Resilience:** Chaos-native architecture; graceful degradation over crashing.
- **Institutional Discipline:** We refuse to trade in toxic liquidity conditions.

### 🧠 Cognitive Decision Heuristics (Integration V1.3)
- **Uncertainty over Prediction:** Ask "does this setup have positive expectancy?"
- **Invalidation-First Thinking:** Every thesis begins with "Where is this wrong?"

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 Architecture (V7.1 Phoenix Hybrid Kernel)
Project Phoenix moves from pure Python to a **Rust-Python Polyglot Microkernel** designed for extreme performance.
- **Sovereign Ingress (Rust):** High-speed TCP/TLS Gateway (AES-256-GCM).
- **The Event Bus (Rust):** Lock-free, single-producer multi-consumer (SPMC) ring buffer. Zero-allocation.
- **The Compute Engine (Python):** Asyncio workers for AI inference (XGBoost/LightGBM) and Strategy logic via PyO3 bindings.
- **Execution Layer (Rust):** Direct interface to the Universal Broker Adapter (MT5/cTrader/FIX).

### 🧱 Institutional Decision Framework (V2 Dual-Loop)
- **Slow Loop (Context, 1s):** Regime ID (HMM), Macro Assessment, Portfolio Exposure, Strategy Qual. *Output:* Trading Permission Ticket.
- **Fast Loop (Execution, <100µs):** Toxicity Check (VPIN), Risk Check, Execution Authorization, Order Dispatch.

### 🧱 Technical Specifications (V7.1)
- **Core Kernel:** Rust 1.70+ (Tokio Runtime).
- **Logic Layer:** Python 3.11+ (PyO3 Bindings).
- **Security:** AES-256-GCM + SHA-384 HMAC. P-521 Curve for internal Key Exchange.
- **Persistence:** Redis (Hot Cache) + PostgreSQL (Audit) + QuestDB (Telemetry).

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Order Flow Toxicity Framework (V1.12)
- **VPIN (Volume-Synchronized PIN):** Probability of informed flow.
- **Imbalance Ratio:** Real-time bid/ask volume divergence.
- **Rule:** If Toxicity Score > Threshold -> Instantaneously flat and disable entries.

### 🧠 ML Architecture V3
- **Primary:** XGBoost/LightGBM (Python training -> ONNX export -> Rust execution).
- **Online Learning:** River (Python) for Hoeffding Adaptive Trees on tick streams.
- **Circuit Breakers:** Disable model for 24h if price drops > 0.2% within 10s of a "Long" prediction.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V3 (Reactive)
- **Layer 1: Execution Risk** (Latency check: if order > 200ms, abort).
- **Layer 2: Symbol Risk** (Volatility regime monitoring).
- **Layer 3: Currency Correlation** (Net exposure tracking).
- **Layer 4: Drawdown Velocity** (If DD drops from 2% to 4% in 1 min -> Global Halt).

### 🛑 Kill Switch Hierarchy (Automated V7.1)
- **Level 1: Soft Halt** (Strategy/Model specific).
- **Level 2: Broker Isolation** (Disconnect failing broker, maintain others).
- **Level 3: Global Liquidation** (Flatten all positions).
- **Level 4: Core Dump & Halt** (System instability detected).

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Universal Broker Abstraction
- **BrokerAdapter Trait:** Standardized Rust interface for `connect`, `subscribe`, `place_order`, and `close`.
- **Implementations:** `MT5Adapter`, `cTraderAdapter`, `FIXAdapter`.
- **Mock Adapter:** Mandatory chaos testing for simulating latency, re-quotes, and drops.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure.*

- **DataHub HA (Hot-Standby):** Primary writes to Redis Stream; Secondary reads/mounts state on failover via Virtual IP.
- **Chaos engineering:** Automated "Game Days" in paper trading (Random process kills, Latency spikes, Data corruption).

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V7.1 Engineering)
*The 4-Quarter Engineering Blueprint.*

### 📍 Q1: The Kernel Rewrite (Foundational)
- Initialize Rust workspace, implement Lock-Free Event Bus, and upgrade to AES-256-GCM.
- Build PyO3 bindings for Python logic integration.

### 🚀 Q2: The Abstraction & Persistence
- Implement Universal Broker Interface and migrate from SQLite to PostgreSQL/Redis.
- Build the "Slow Loop" Context Engine.

### 🌐 Q3: The "Fast Loop" & Toxicity
- Implement VPIN/Toxicity Engine in Rust.
- Integrate ONNX Runtime for zero-copy inference in the execution path.

### 🛡️ Q4: Resilience & UI
- Deploy Chaos Monkey and launch **FinCon Terminal V2** (Next.js/WebSockets).
- Automate L99 Certification (CSCV/Deflated Sharpe).

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Analysis Paralysis** | High | Severe | **Slow/Fast Loop separation**. |
| **Broker Capture** | Medium | Catastrophic | **Universal Broker API** abstraction. |
| **Internal Jitter** | Medium | Severe | **Rust Kernel** implementation. |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
