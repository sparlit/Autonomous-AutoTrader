# 🪐 Project Phoenix: Sovereign Execution Engine (V1.5)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.5 (Institutional Reality Audit)
**Focus:** Operational Excellence over Architectural Vanity.

✅ **Production Stable Core (MVP Scope)**
🔄 **Institutional Governance Layer Under Refinement**
🔄 **Adaptive Multi-Asset Trading Platform (FX Focus Phase 1)**
🔄 **Research Extensions Under Continuous Validation**

⚠️ **CRITICAL NOTE:** V1.5 (based on the V7.1.0 Rebuilt Sovereign) represents a pivot focused on operational excellence. The project has discarded architectural vanity in favor of survivability and capital preservation.

✅ **Core Integrity:** Modular Monolith Architecture (Phased Implementation)
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf)
✅ **Standard:** L99-Standard V2 Certified Framework
🟡 **Hardening:** Implementation of 10-Layer Institutional Stack (In-Progress)

### 🧐 Institutional Reality Audit (Integration V1.5)
Project Phoenix V7.1.0 is built on the ruins of over-ambitious drafts. We acknowledge these brutal truths:
1.  **MT5 is a Retail Trap:** B-book brokers conflict with client success. Phase 1 proves logic on MT5; Phase 2 migrates to **FIX Gateway** for true institutional liquidity.
2.  **SQLite is not for Audit:** Institutional compliance requires ACID-compliant, replicated storage. **PostgreSQL** is now the mandatory governance store.
3.  **Custom Event Buses Deadlock:** The legacy `bus.py` is deprecated. **Redis Streams** with consumer groups and **Protobuf** schemas provide the production backbone.
4.  **The ML Frankenstein is Dead:** Removed FinBERT/FAISS/RL bloat. Simplified to **XGBoost + LSTM** for production stability.
5.  **Compliance is not an Add-on:** MiFID III, Basel FRTB, and GDPR audit trails are built into the core hashing chains from Day 1.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Executive Summary: The Brutal Truth**
Project Phoenix is architecturally ambitious but operationally naive. It reads like a master's thesis on what an institutional trading platform *should* look like, written by someone who has never operated one under live market conditions with real capital at risk.
**Critical Finding:** The project has a 73% theoretical completeness score but only a 31% operational readiness score. The gap between "designed" and "deployable" is where most algorithmic trading platforms die.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries that the platform must operate within. These are critical for aligning development with long-term capital preservation.*

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance, execution discipline, and adaptive market participation.

**Scope Constraint (V7.1.0):** V7.1.0 focuses exclusively on retail FX via MT5 as the MVP execution venue. FIX 4.4/5.0 gateway is Phase 2. Multi-asset expansion is Phase 3.

### 📊 Performance Mandates (Realistic & Phased)
| Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **MAR Ratio** | > 0.8 | > 1.5 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | **CRITICAL** |

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Performance Target Critique:**
The Sharpe > 2.0, Sortino > 3.0, and Max DD < 5% targets are described as mathematically aggressive.
**God's Solution for Realistic Targets:**
- Sharpe > 1.0 (achievable with discipline).
- Sortino > 1.5 (accounts for tail risk).
- MAR > 0.8 (conservative but achievable).
- Max DD < 10% (retail FX reality).
- Risk of Ruin < 1% over 5 years.

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget to prevent over-engineering, the Edge Attribution Framework to ensure every trade has a proven statistical basis, and the Stability Paradox Resolution to manage the trade-off between innovation and reliability.*

### 💎 Core Values (V7.1.0)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Performance:** Sub-100ms internal event latency (Python + MT5).
- **Resilience:** Defensive architecture designed to survive market volatility and adversarial broker behavior.
- **Institutional Discipline:** Capital preservation is primary; profit is a secondary outcome.
- **Regulatory Compliance:** Built-in from day one.

### 🧠 Cognitive Decision Heuristics (Integration V1.3)
Professional trading logic is built on **Thinking Structures**, not just strategies:
- **Uncertainty over Prediction:** Ask "does this setup have positive expectancy?"
- **Invalidation-First Thinking:** Every thesis begins with "Where is this wrong?"
- **Environmental Awareness:** Volatility, timing, and macro context assessed *before* trade triggers.

To combat the **"Conspiracy of Complexity"** and false certainty, V1.5 enforces:

### A. The Simplicity Budget
Every subsystem must justify its operational burden. If **(Alpha + Risk Reduction) < (Maintenance Cost + Failure Surface)**, it is removed.

### B. The Edge Attribution Framework
Every signal must prove its incremental value:
`Signal → Decision Change → Trade Outcome Change → Portfolio Alpha Improvement.`

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy. This section is vital for maintaining architectural consistency across the modular monolith.*

Project Phoenix utilizes a **Modular Monolith** architecture with clean service boundaries.

### 🧩 System Overview (V1.5 Refinement)
- **Sovereign Ingress:** AES-256-GCM Secure Gateway. MT5 (Phase 1) → FIX Protocol Priority (Phase 2).
- **Persistence Layer:** PostgreSQL (ACID Governance) + QuestDB (Telemetry) + Redis Cluster (Hot State).
- **Event Bus:** Redis Streams with **Protocol Buffers (Protobuf)** for type-safe message passing and schema validation via Buf Registry.
- **Decision Engine Engine:** Split into **Context Loop** (Slow/Governance) and **Execution Loop** (Fast/Signal).

### 🧱 Technical Specifications (V7.1.0)
- **Core Engine:** Python 3.11+ FastAPI Orchestrator (synchronous core, async analytics).
- **Security:** JWT RBAC + AES-256-GCM Encryption (CBC deprecated).
- **Persistence:** PostgreSQL 15+, QuestDB 7+, Redis Cluster 7+, S3-Compatible Storage.
- **Event Bus:** Redis Streams (exactly-once processing with consumer groups).

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation. This section ensures that all trading models are statistically sound and have a high probability of success in live markets.*

### 🧠 ML Architecture V2 (Simplified)
- **Primary Model:** XGBoost (Target: 1-hour forward return terciles).
- **Secondary Model:** LSTM (Target: 1-hour realized volatility).
- **Removed:** FinBERT/FAISS/RL bloat removed for production stability.

### 🔬 The Phoenix Gauntlet (Model Governance V7.1.0)
Promotion path with explicit gates:
**Research → Backtest → Validation → Walk Forward → Incubation → Shadow Trading → Production.**

- **Drift Detection:** PSI, Feature/Label Drift, Regime Drift, Prediction Drift.
- **Reality Verification Engine:** Continuous measurement of Win Prob, R/R, Drawdown. Persistent degradation (2 months) reduces model authority.

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

**Conflict Resolution:** Higher precedence always wins.
**Validation:** Pre-trade **Monte Carlo simulation** is mandatory for all executions.

### 🛑 Kill Switch Hierarchy (Simplified V1.5)
1. **Level 1 (Strategy):** Halt specific strategy on volatility or drawdown breach.
2. **Level 2 (Symbol):** Freeze symbol on extreme spread or data gaps.
3. **Level 3 (Global):** Flatten all positions and disable entry.
4. **Level 4 (Infrastructure):** Safe-Mode disconnect on heartbeat failure or audit corruption.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers. This includes FIX protocol implementation, slippage analytics, and the Almgren-Chriss model for optimal order execution. It ensures the system minimizes transaction costs.*

### 🏛️ Liquidity Inference & Decision Framework
- **Liquidity Framework:** Observed (L2), Estimated (Spread/Tick), Hypothesized (Structural).
- **Decision Engine sequence:** Market Condition → Liquidity Mapping → Incentive Analysis → Invalidation Check → Execution Qualification.
- **Sovereign Solution:** FIX 4.4/5.0 gateway priority in Phase 2 to exit the "Retail Trap".

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure. This includes the 'Dead-Man Switch', autonomous recovery procedures, and the use of chaos engineering to proactively identify weaknesses.*

- **DataHub High Availability:** Raft consensus (etcd/Consul) + Patroni/PostgreSQL Master-Standby.
- **Chaos Engineering:** Daily automated experiments; system must survive 1000 trials without capital loss.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR). This section details the cryptographic hashing of the audit trail (Merkle Chains) to provide undeniable proof of execution.*

- **Audit Trail:** JSON/Avro, append-only WORM, SHA-256 hash chains.
- **Compliance Matrix:** MiFID III algorithmic trading requirements, Basel III FRTB P&L attribution.

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
- [ ] Deploy **XGBoost + LSTM** production ensemble.
- [ ] **Kill Criterion:** If Sharpe < 0.5 in 6 months live, pivot or abandon.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- [ ] Implement **FIX Gateway** for institutional liquidity.
- [ ] Multi-broker orchestration and conflict detection.

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- [ ] Launch **FinCon Terminal** (React/Next.js dashboard).
- [ ] Full MiFID III/Basel audit compliance certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- [ ] Prime Broker integration and external capital on-boarding.

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **MQL5 Dependency** | High | Severe | Primary FIX Gateway + MT5 Fallback. |
| **Adversarial Broker** | High | Severe | A-book/B-book monitoring + Conflict Detection. |
| **Team Burnout** | Medium | Severe | Standardized documentation + 8-person redundancy. |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
