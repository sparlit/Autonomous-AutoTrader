# 🪐 Project Phoenix: Sovereign Execution Engine (V1.6)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.6 (Survivability Realignment)
**Focus:** Survivability under Model Failure & Operational Excellence.

✅ **Production Stable Core (MVP Scope)**
🔄 **Institutional Governance Layer Under Refinement**
🔄 **Adaptive Multi-Asset Trading Platform (FX Focus Phase 1)**
🔄 **Research Extensions Under Continuous Validation**

⚠️ **CRITICAL NOTE:** V1.6 represents a fundamental realignment around **Survivability under Model Failure**. We acknowledge that no amount of governance can eliminate market uncertainty; therefore, the system is designed to survive when models fail, not just succeed when they work.

✅ **Core Integrity:** Modular Monolith Architecture (Phased Implementation)
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf)
✅ **Standard:** L99-Standard V2 Certified Framework
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (In-Progress)

### 🧐 Institutional Reality Audit (Integration V1.5)
Project Phoenix V7.1.0 is built on the ruins of over-ambitious drafts. We acknowledge these brutal truths:
1.  **MT5 is a Retail Trap:** B-book brokers conflict with client success. Phase 1 proves logic on MT5; Phase 2 migrates to **FIX Gateway**.
2.  **SQLite is not for Audit:** Institutional compliance requires ACID-compliant, replicated storage. **PostgreSQL** is mandatory.
3.  **Custom Event Buses Deadlock:** The legacy `bus.py` is deprecated. **Redis Streams** with consumer groups and **Protobuf** provide the backbone.
4.  **The ML Frankenstein is Dead:** Removed FinBERT/FAISS/RL bloat. Simplified to **XGBoost + LSTM**.
5.  **Compliance is not an Add-on:** MiFID III, Basel FRTB, and GDPR audit trails are built into the core hashing chains.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Executive Summary: The Brutal Truth**
Project Phoenix is architecturally ambitious but operationally naive. The gap between "designed" and "deployable" is where most algorithmic trading platforms die.
**Critical Finding:** False certainty created by architectural sophistication is the biggest existential threat.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries that the platform must operate within. These are critical for aligning development with long-term capital preservation.*

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance and execution discipline.

**Scope Constraint:** V7.1.0/V1.6 focuses exclusively on retail FX via MT5 as the MVP execution venue. FIX 4.4/5.0 gateway is Phase 2. Multi-asset expansion is Phase 3.

### 📊 Performance Mandates (Realistic & Phased)
| Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **MAR Ratio** | > 0.8 | > 1.5 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | **CRITICAL** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget to prevent over-engineering, the Edge Attribution Framework to ensure every trade has a proven statistical basis, and the Stability Paradox Resolution to manage the trade-off between innovation and reliability.*

### 💎 Core Values (V1.6 Realignment)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Simplicity Budget:** Every subsystem must justify its operational burden: `(Alpha + Risk Reduction) < (Maintenance Cost + Failure Surface)`.
- **Edge Attribution:** Every signal must prove its incremental value from Decision Change to Portfolio Alpha improvement.
- **Probabilistic Regime Awareness:** Replace binary regime detection with a Probabilistic State Machine (e.g., 70% Trend, 20% Range, 10% Crisis) to scale risk continuously.

### 🧠 Cognitive Decision Heuristics (Integration V1.3)
Professional trading logic is built on **Thinking Structures**:
- **Uncertainty over Prediction:** Ask "does this setup have positive expectancy?"
- **Invalidation-First Thinking:** Every thesis begins with "Where is this wrong?"
- **Environmental Awareness:** Volatility, timing, and macro context assessed *before* trade triggers.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 The 12-Layer Institutional Stack (V1.6 Expansion)
- **Layer 0: Data Quality Firewall** (Tick validation, Gap/Duplicate detection, Spread anomaly).
- **Layer 1: Market Data Layer** (Binary MsgPack / Protobuf).
- **Layer 2: Liquidity Intelligence** (Observed/Estimated Liquidity, mapping SL clusters).
- **Layer 3: Strategy Layer** (Alpha Validation Engine: Models must prove incremental value).
- **Layer 4: Portfolio Construction** (Capital Allocation, Risk/Correlation Budgeting).
- **Layer 5: Risk Engine** (7-Layer Stack + Exposure Graph).
- **Layer 5.5: Model Governance** (PSI Monitoring, Shadow Mode).
- **Layer 5.6: Meta-Governance** (Governing the governance: Monitor Drift Detector accuracy).
- **Layer 6: Execution Intelligence** (Almgren-Chriss, Fill Prob, Cost Attribution).
- **Layer 7: Broker Mesh** (Primary/Secondary/Tertiary failover).
- **Layer 8: Recovery Engine** (Autonomous Failure Detection, Repair, and Validation).
- **Layer 9: Audit & Explainability** (Merkle-Chained Provenance + Decision Graphs).

### 🧩 Persistence & Event Sourcing (V1.6)
- **Audit/Governance:** PostgreSQL (ACID-compliant, replicated).
- **Telemetry:** QuestDB (Time-series).
- **Event Bus:** Redis Streams with Protobuf. Replace centralized bottlenecks with **Domain Event Buses** (Market, Risk, Execution, etc.).
- **Event Sourcing Spec:** Mandatory Versioned Events, Replay Engine, Snapshots, and Compaction.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation. This section ensures that all trading models are statistically sound and have a high probability of success in live markets.*

### 🔬 The Alpha Validation Engine (V1.6)
Every model must pass an incremental value check before deployment:
- **Incremental Sharpe/MAR**
- **Incremental Drawdown Reduction**
- **Incremental Expectancy**

### 🧠 ML Architecture & Model Governance
- **Simplified Stack:** XGBoost + LSTM. Remove FinBERT/RL for production.
- **Online Learning Safety:** Online models never touch production directly. Flow: `Online -> Shadow -> Validation -> Promotion`.
- **Meta-Governance:** Monitor the accuracy of Drift Detectors, Regime Classifiers, and Confidence Calibration.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section of the blueprint. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches (Levels 1-4). This is the 'Shield' of the sovereign engine.*

### 🛡️ The 7-Layer Risk Stack (Precedence)
1. **Layer 5: Portfolio Risk** — Global exposure, correlation stress.
2. **Layer 4: Currency Risk** — Single currency concentration.
3. **Layer 3: Symbol Risk** — Single pair exposure.
4. **Layer 2: Strategy Risk** — Strategy-level drawdown.
5. **Layer 1: Trade Risk** — Single trade size, SL/TP.
6. **Layer 6: Broker Risk** — Broker health, execution quality.
7. **Layer 7: Infrastructure Risk** — System health, connectivity.

### 📊 Exposure Graph Engine (V1.6 Expansion)
Beyond current exposure, the engine must track:
- **Factor/Sector Exposure**
- **Volatility/Correlation Exposure**
- **Tail/Broker/Strategy Exposure**

### 🛑 Kill Switch Decision Tree (V1.6)
Kill switches are not single-action. The decision tree includes:
- **Liquidate** (Close all)
- **Reduce** (Downsize)
- **Freeze** (Stop new entries)
- **Hedge** (Neutralize delta)
- **Human Review** (Mandatory authorization)

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers. This includes FIX protocol implementation, slippage analytics, and the Almgren-Chriss model for optimal order execution.*

### 🏛️ Liquidity & Broker Mesh (V1.6)
- **Broker Mesh:** Primary, Secondary, and Tertiary brokers with automatic migration/failover.
- **Execution Intelligence:** Cost Attribution Engine tracking Spread, Commission, Swap, Latency, and Slippage costs per strategy.
- **Capacity Analysis:** Tracking Maximum Position Size, Daily Volume, and Market Impact.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure. This includes the 'Dead-Man Switch', autonomous recovery procedures, and the use of chaos engineering to proactively identify weaknesses.*

### 📍 Autonomous Recovery Engine (V1.6)
The system does not just survive failure; it repairs itself through:
- **Failure Detection & Root Cause Analysis**
- **Automated Repair & Validation**
- **Recovery Verification**

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR). This section details the cryptographic hashing of the audit trail (Merkle Chains) to provide undeniable proof of execution.*

### ⚖️ Explainability Specification (V1.6)
Audit trails are extended into Decision Provenance Graphs:
- **Decision Graph:** Full path from signal to execution.
- **Risk/Model Attribution:** Quantifying the contribution of each layer/model to the final decision.
- **Execution Attribution:** Measuring the quality of execution against benchmarks.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform. This ensures the project is adequately staffed and funded for long-term sustainability.*

### 👥 Minimum Viable Team (8 People)
1x Lead Architect, 2x Backend/Kernel Engineers, 1x Quant Dev, 1x DevOps/SRE, 1x QA/SDET, 1x Risk/Compliance, 1x Operations/Terminal Manager.

---

## 🗺️ 11. Strategic Roadmap & Phase Progression
*The chronological plan for the project's evolution. It provides a clear path from the initial MVP to a fully scaled, multi-asset institutional trading platform.*

### 📍 Phase 1: MVP & Logic Proof (Months 0-6)
- [ ] Implement **Modular Monolith Core** on PostgreSQL/Redis.
- [ ] Deploy **Data Quality Firewall** and **Alpha Validation Engine**.
- [ ] **Kill Criterion:** If Sharpe < 0.5 in 6 months live, pivot or abandon.

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **MQL5 Dependency** | High | Severe | Primary FIX Gateway + MT5 Fallback. |
| **Adversarial Broker** | High | Severe | A-book/B-book monitoring + Broker Mesh. |
| **Complexity Overload** | High | Severe | **Simplicity Budget** enforcement. |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
