# 🪐 Project Phoenix: Sovereign Execution Engine (V1.13)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.13 (V7.0.0 Specification Alignment)
**Focus:** Full Institutional Stack Integration & Model Governance.

✅ **Production Stable Core (MQL5/Python Integrated)**
✅ **Institutional Governance Layer (Active)**
✅ **Adaptive Multi-Asset Trading Platform (FX Focus)**
🔄 **Research Extensions Under Continuous Validation**

⚠️ **CRITICAL NOTE:** V1.13 integrates the full **V7.0.0 Functional Specification**. While maintaining the "Hybrid Kernel" and "Ruthless Pragmatism" of earlier versions, we now codify the institutional-grade Model Governance (Layer 5.5) and the 12-layer stack hardening requirements.

✅ **Core Integrity:** Modular Monolith / Hybrid Kernel.
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf) + Event Sourcing.
✅ **Standard:** L99-Standard V3 / Certification Framework V2.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (Active Implementation).

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient trading platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance, execution discipline, and adaptive market participation.

### 📊 Performance Mandates (Tiered Milestones)
| Metric | Phase 1 Target | V7.0.0 Stretch | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **MAR Ratio** | > 0.8 | > 1.5 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | **CRITICAL** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Values (Pragmatic + Institutional)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Performance:** Sub-millisecond internal event latency (Internal Rust Kernel optimized).
- **Resilience:** Defensive architecture designed to survive market volatility and network instability.
- **Institutional Discipline:** Capital preservation is the primary objective.

### ⚖️ Reinforcement Learning Policy (V7.0.0)
RL systems may not directly control capital. Approved workflow:
`RL Recommendation → Risk Engine Validation → Position Authorization → Execution`.
Risk constraints are immutable.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 V7.0 Phoenix Architecture (Hybrid Kernel)
- **Sovereign Ingress:** AES-256-GCM Secure Gateway for all MQL5/FIX traffic.
- **DataHub HA Architecture:** Primary + Secondary + Event Journal + Replay Queue (Zero data loss).
- **The Nervous System (Rust):** Lock-free event bus and order execution layer.
- **The Compute Engine (Python):** Model Governance and Inference workers.

### 🧱 Technical Specifications (V1.13 Unified)
- **Core Engine:** Python 3.11+ FastAPI + Rust 1.70+ Tokio.
- **Persistence:** Relational Audit (PostgreSQL) + High-frequency Telemetry (QuestDB) + Event Journal.
- **Inference:** ONNX Runtime for INT8 quantized XGBoost and Transformer models.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Structural Market Intelligence (V7.0.0)
- **Liquidity Framework:** Classification into Observed, Estimated, and Hypothesized liquidity. Inference over Prediction.
- **Market Regime Engine V2:** 10 supported states (Trend L/H Vol, Range L/H Vol, Compression, Expansion, Crisis, Event Driven, Transition, Unknown).

### 🧠 Layer 5.5 — Model Governance Engine
Supervises all predictive systems with the following responsibilities:
- **Drift Detection:** PSI, Feature, Label, Regime, and Prediction Drift. Threshold breach = Shadow Mode.
- **Confidence Decay:** Dynamic scores decay with age. Lack of retraining reduces model authority.
- **Champion–Challenger:** Research → Validation → Walk Forward → Shadow Trading → Challenger → Champion.
- **Reality Verification:** Records Expected vs Actual (Win Prob, R/R, Duration, DD).

### 🧠 Macro Intelligence Layer
Dedicated engine monitoring CPI, NFP, FOMC, GDP, etc.
- **Behavior:** Reduce Risk, Restrict Entries, Increase Spread Protection, and Resume only after stabilization.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V2
**Multi-Layer Risk Stack:**
1. Trade Risk | 2. Strategy Risk | 3. Symbol Risk | 4. Currency Risk | 5. Portfolio Risk | 6. Broker Risk | 7. Infrastructure Risk.
Any layer may independently halt trading.

### 📊 Exposure Graph Engine (V7.0.0 Enforced)
Computes true exposure (e.g., netting EURUSD/GBPUSD/AUDUSD into USD Short). Global limits enforced for USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD.

### 🛑 Kill Switch Hierarchy (V7.0.0)
- Level 1: Strategy Halt | Level 2: Symbol Halt | Level 3: Portfolio Freeze | Level 4: Broker Isolation | Level 5: Emergency Liquidation | Level 6: Safe Mode | Level 7: Human Auth Required.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Institutional Decision Framework (V7.0.0)
8-stage constrained process:
1. Regime ID → 2. Liquidity Inference → 3. Macro Assessment → 4. Portfolio Exposure → 5. Strategy Qual → 6. Risk Qual → 7. Execution Qual → 8. Position Authorization.
**Failure at any stage = Immediate Veto.**

### 🏥 Broker Health & Execution Analytics
- **Execution Analytics Engine:** Monitors Fill Rate, Slippage, Spread Conditions (Normal/Elevated/Extreme), Latency, and Reject Rate.
- **Broker Health Engine:** Continuous scoring based on stability and spread. Risk scales automatically with broker quality.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure.*

### 🧪 Chaos Engineering Framework (V7.0.0)
Continuous testing for:
- MT5 Disconnect | Network Split | Tick Delay | Data Corruption | Database Failure | Worker Crash | Clock Drift.
**Goal:** Survive all tests without capital loss.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

### ⚖️ L99 Certification Framework V2
- L99-A: Code Integrity | L99-B: Infrastructure Reliability | L99-C: Risk Management | L99-D: Execution Quality | L99-E: Research Validation | L99-F: Resilience & Recovery.

### ⚖️ Institutional Audit Trail
Decision Provenance records: *Why Trade? Why Now? Why Size? Why Stop? Why Target? Why Confidence? Why Regime? Why Exposure?*
The platform is designed to be explainable, auditable, and falsifiable at every level.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform.*

### 👥 Team & Roles (V7.0.0)
- **Architect:** Lead Designer of the Microkernel and Event-Driven logic.
- **Quant Engineer:** Liquidity Inference logic and AI model training/quantization.
- **Security Specialist:** AES encryption, RBAC, and Audit integrity.
- **UI/UX Designer:** Crafting the "FinCon Terminal" (Bloomberg-class Cockpit).
- **Ops Engineer:** Monitoring, Chaos, and On-call (V1.9 Integration).

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V1.13)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Institutional Core & Governance
- [x] Resolve EventBus dependencies, standardize security.
- [ ] Implement **Model Governance Engine (Layer 5.5)**.
- [ ] Finalize **DataHub HA Architecture** with Event Journaling.
- [ ] Integrate **Exposure Graph Engine** for global risk enforcement.

### 🚀 Phase 2: Advanced Liquidity & Intelligence
- [ ] Deploy Execution Analytics & Broker Health Engines.
- [ ] Integrate **Macro Intelligence Layer** (Automatic risk reduction).
- [ ] Implement **Wyckoff Phase Detection** and Similarity Search (FAISS).

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Model Drift** | High | Severe | **Model Governance Engine (Layer 5.5)**. |
| **Broker Adverse Selection** | Medium | Catastrophic | **Broker Health Engine** scoring. |
| **Technical Debt** | Medium | Severe | **L99 Certification** automation. |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
