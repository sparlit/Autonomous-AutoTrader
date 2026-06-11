# 🪐 Project Phoenix: Sovereign Execution Engine (V1.2)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.2 (Institutional Realignment)
**Focus:** Operational Feasibility over Architectural Elegance.

✅ **Production Stable Core (MVP Scope)**
🔄 **Institutional Governance Layer Under Refinement**
🔄 **Adaptive Multi-Asset Trading Platform (FX Focus Phase 1)**
🔄 **Research Extensions Under Continuous Validation**

⚠️ **CRITICAL NOTE:** V1.2 represents a ground-up rebuild focused on operational feasibility over architectural elegance. All features must directly contribute to capital preservation or regulatory compliance.
**Operational Mode:** Phoenix V1.0 (Master Blueprint)
**Focus:** Survivability under Model Failure & Operational Feasibility.

✅ **Core Integrity:** Modular Monolith Architecture (MVP Stabilized)
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf)
✅ **Standard:** L99-Standard V2 Certified Framework
🟡 **Hardening:** Implementation of 10-Layer Institutional Stack (In-Progress)

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Executive Summary: The Brutal Truth**
Project Phoenix is architecturally ambitious but operationally naive. It reads like a master's thesis on what an institutional trading platform *should* look like, written by someone who has never operated one under live market conditions with real capital at risk. The document is heavy on vision, light on execution mechanics, and dangerously silent on several existential risks that would kill the project before it reaches production.
**Critical Finding:** The project has a 73% theoretical completeness score but only a 31% operational readiness score. The gap between "designed" and "deployable" is where most algorithmic trading platforms die.

**L99 Certification Gap Analysis:**
- **L99-A (Code):** Requires 100% unit test coverage, 80% integration coverage, 0 critical SonarQube issues.
- **L99-B (Infra):** Requires 99.99% uptime, <5 second failover, automated recovery.
- **L99-C (Risk):** Zero uncontrolled drawdowns >2%, all kill switches tested weekly.
- **L99-D (Execution):** Slippage < 1 pip vs benchmark, fill rate > 95%.
- **L99-E (Research):** All strategies pass White Reality Check, PBO < 0.05.
- **L99-F (Resilience):** Survive 1000 chaos experiments, RTO < 5s for critical systems.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries that the platform must operate within. These are critical for aligning development with long-term capital preservation.*

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance, execution discipline, and adaptive market participation.

**Scope Constraint (V7.1.0):** V7.1.0 focuses exclusively on retail FX via MT5 as the MVP execution venue. FIX 4.4/5.0 gateway is Phase 2. Multi-asset expansion is Phase 3. This constraint is non-negotiable for operational feasibility.

### 📊 Performance Mandates (Realistic & Phased)
| Metric | Target | Reality Check | Status |
*Defines the key performance indicators (KPIs) for the trading engine. These metrics are the yardstick for project success.*

| Metric | Phase 1 (Reality) | Phase 2 (Stretch) | Status |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 aspirational after 2 years live | Phase 1 |
| **Sortino Ratio** | > 1.5 | > 3.0 aspirational after 2 years live | Phase 1 |
| **MAR Ratio** | > 0.8 | > 1.5 aspirational after 2 years live | Phase 1 |
| **Max Drawdown** | < 10% | < 5% aspirational after 2 years live | **ABSOLUTE** |
| **Risk of Ruin** | < 1% | < 0.1% aspirational after 2 years live | **ABSOLUTE** |
| **Capital Preservation** | Absolute | Absolute | **CORE** |

**Target Rationale:** Initial targets reflect retail FX reality with MT5 execution costs. Targets tighten as execution quality improves (FIX gateway, broker diversification).

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Performance Target Critique:**
The Sharpe > 2.0, Sortino > 3.0, and Max DD < 5% targets are described as mathematically aggressive and potentially inconsistent at reasonable position sizes.
**God's Solution for Realistic Targets:**
- Sharpe > 1.0 (achievable with discipline)
- Sortino > 1.5 (accounts for tail risk)
- MAR > 0.8 (conservative but achievable)
- Max DD < 10% (retail FX reality)
- Risk of Ruin < 1% over 5 years
- Benchmark: HFRX Macro/CTA Index or Barclay Currency Traders Index
- Kelly Criterion: Use half-Kelly for position sizing.

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget to prevent over-engineering, the Edge Attribution Framework to ensure every trade has a proven statistical basis, and the Stability Paradox Resolution to manage the trade-off between innovation and reliability.*

### 💎 Core Values (V7.1.0)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Performance:** Sub-100ms internal event latency (realistic for Python + MT5). Sub-millisecond is Phase 2 (C++ engine).
- **Resilience:** Defensive architecture designed to survive market volatility, network instability, and adversarial broker behavior.
- **Institutional Discipline:** Capital preservation is the primary objective; profit is a secondary outcome of discipline.
- **Regulatory Compliance:** Built-in compliance from day one, not as an afterthought.

To combat the **"Conspiracy of Complexity"** and false certainty, V1.2 enforces:
To combat the **"Conspiracy of Complexity"** and false certainty, V1.0 enforces:

### A. The Simplicity Budget
Every subsystem must justify its operational burden. If **(Alpha + Risk Reduction) < (Maintenance Cost + Failure Surface)**, it is removed. We prioritize a "Working Core" over "Comprehensive Features."

### B. The Edge Attribution Framework
Every signal must prove its incremental value:
`Signal → Decision Change → Trade Outcome Change → Portfolio Alpha Improvement.`

### C. The Stability Paradox Resolution
Status checkmarks (`✅`) are strictly reserved for code that has passed L99-Standard verification. Aspirational goals stay in the roadmap.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Microkernel Critique:**
The "multi-layer Event-Driven Asynchronous Microkernel" is identified as over-engineered for retail FX.
**God's Solution:**
- Simplify to a Modular Monolith with clean boundaries.
- Use FastAPI for API layer, Celery for background jobs, Redis for caching/messaging.
- Separate Core Engine (synchronous, deterministic) from Analytics (async, best-effort).
- Rule: If a component doesn't directly protect capital, it doesn't exist in V1.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy. This section is vital for maintaining architectural consistency across the modular monolith.*

Project Phoenix utilizes a **Modular Monolith** architecture with clean service boundaries, focused on operational simplicity and capital preservation.

### 🧱 Technical Specifications (V7.1.0)
- **Core Engine:** Python 3.11+ FastAPI Orchestrator (synchronous core, async analytics)
- **Persistence:**
  - PostgreSQL 15+ (Audit trail, configuration, risk limits — ACID, replicated)
  - QuestDB 7+ (High-frequency telemetry, time-series analytics)
  - Redis Cluster 7+ (Caching, session state, real-time messaging)
  - S3-Compatible Object Storage (Backups, event archives, model artifacts)
- **Inference:** ONNX Runtime for INT8 quantized models (CPU-optimized)
- **Event Bus:** Redis Streams (exactly-once processing with consumer groups)
- **Schema Registry:** Buf Schema Registry (Protobuf) with backward compatibility enforcement
- **Message Format:** Protocol Buffers (binary, efficient, schema-evolution friendly)

### 🔐 Security Architecture (V7.1.0)
- **Zero Trust Network:** All internal communication authenticated and encrypted.
- **HSM Integration:** Hardware Security Module for private key storage (YubiHSM 2 minimum).
- **Secret Management:** HashiCorp Vault or AWS Secrets Manager.
- **Data Encryption:** At-rest (AES-256-GCM), in-transit (TLS 1.3), in-use (memory encryption).
- **Audit Security:** Cryptographic hash chains (SHA-256) with Merkle tree verification.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Persistence Layer & Event Bus Gaps:**
- **Audit Layer:** Move from SQLite to PostgreSQL with streaming replication (minimum 2 replicas).
- **Telemetry:** QuestDB + automated partitioning by date.
- **Event Store:** Replace custom bus with Redis Streams or Apache Kafka; use Buf Schema Registry for Protobuf.
- **Snapshot Store:** Redis Cluster for fast state recovery.
- **Data Quality:** Implement multi-broker feed cross-validation and automated checks for outliers/inconsistencies.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation. This section ensures that all trading models are statistically sound and have a high probability of success in live markets.*

### 🧠 ML Architecture V2 (Simplified)
- **Primary Model:** XGBoost (offline, nightly retraining)
  - Target: 1-hour forward return terciles (up/neutral/down)
  - Validation: Walk-forward analysis with 10-fold expanding window
  - Retraining: Incremental update using xgboost.QuantileDMatrix
- **Secondary Model:** LSTM (volatility forecasting)
  - Target: 1-hour realized volatility
  - Architecture: 2-layer LSTM, 64 hidden units, dropout 0.2

### 🔬 The Phoenix Gauntlet (Model Governance V7.1.0)
Promotion path with explicit gates:
**Research → Backtest → Validation → Walk Forward → Incubation → Shadow Trading → Production.**

- **Drift Detection:** PSI, Feature/Label Drift, Regime Drift, Prediction Drift.
  - **Yellow Alert:** Increase monitoring, -20% position size.
  - **Orange Alert:** Shadow mode (10% allocation).
  - **Red Alert:** Halt strategy, manual revalidation.
- **Confidence Decay:** Dynamic scores decay with age (5%/month after 6 months).
- **Reality Verification Engine:** Continuous error measurement; degradation threshold = 2 months.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Model Governance & Statistical Mirage:**
- **Explicit Gates:** Research (5y data), Validation (Deflated Sharpe > 1.0, PBO < 0.1), Walk Forward (10-fold), Shadow (200 trades/90 days).
- **ML Architecture:** Start simple with XGBoost (direction) and LSTM (volatility). Remove FinBERT and RL from production until proven.
- **Validation Parallelization:** Run research/backtest/validation simultaneously; use temporal holdout.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section of the blueprint. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches (Levels 1-4). This is the 'Shield' of the sovereign engine.*

### 🛡️ The 7-Layer Risk Stack (Precedence)
1. **Layer 5: Portfolio Risk** — Global exposure, correlation stress
2. **Layer 4: Currency Risk** — Single currency concentration
3. **Layer 3: Symbol Risk** — Single pair exposure
4. **Layer 2: Strategy Risk** — Strategy-level drawdown, win rate
5. **Layer 1: Trade Risk** — Single trade size, SL/TP
6. **Layer 6: Broker Risk** — Broker health, execution quality
7. **Layer 7: Infrastructure Risk** — System health, connectivity

**Conflict Resolution:** Higher precedence always wins. 2FA required for overrides.
**Latency Budget:** Each layer < 2ms, total < 14ms.

### 📊 Exposure Graph Engine (V7.1.0)
Computes global exposure using **delta-adjusted notional**, **volatility-adjusted exposure**, and **marginal VaR**.
- **Currency Limits:** USD (±30%), EUR (±25%), GBP (±20%), etc.
- **Calculation:** DCC-GARCH correlation matrix + stress testing (2008, 2020, 2022 scenarios).

### 🛑 Kill Switch Hierarchy (Simplified V7.1.0)
- **Level 1: Soft Halt** — No new entries. Trigger: DD > 5% or Broker Health < 50.
- **Level 2: Hard Halt** — Close-only mode. Trigger: DD > 8% or Broker Health < 30.
- **Level 3: Emergency Liquidation** — Close all at market. Trigger: DD > 10% or Broker < 20.
- **Level 4: System Shutdown** — Terminate all. Trigger: Security breach or infrastructure failure.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers. This includes FIX protocol implementation, slippage analytics, and the Almgren-Chriss model for optimal order execution. It ensures the system minimizes transaction costs.*

### 🏛️ Liquidity Inference & Decision Framework
- **Liquidity Framework:** Observed (L2), Estimated (Spread/Tick), Hypothesized (Structural). V7.1.0 uses Observed/Estimated.
- **8-Stage Decision Process:** Regime ID → Liquidity → Macro → Portfolio → Strategy → Risk → Broker → Position Manager. **Failure at any stage = Immediate Veto.**
- **Market Regime Engine V2:** HMM with GARCH. States include Trend, Range, Compression, Expansion, Crisis, etc.

### 🏥 Broker Health & Execution Analytics
- **Health Engine:** Monitors spread stability, slippage, rejection rate, and **conflict of interest** (A-book vs B-book).
- **Execution Optimization:** Pre-trade fill probability, Almgren-Chriss liquidation model, smart order routing (Phase 2).

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**The MQL5 Dependency & Broker Health:**
- **Sovereign Solution:** Add FIX 4.4/5.0 gateway as primary path; MT5 as fallback only. Integrate with institutional ECNs.
- **Conflict Detection:** Monitor for systematic adverse selection.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure. This includes the 'Dead-Man Switch', autonomous recovery procedures, and the use of chaos engineering to proactively identify weaknesses.*

### 📍 DataHub High Availability (V7.1.0)
- **Consensus:** Raft consensus (etcd/Consul) for leader election.
- **DB:** Primary PostgreSQL with 2 standbys (Patroni).
- **Consistency:** CP for Risk/Audit, AP for Telemetry.
- **Clock Drift:** NTP with PTP precision.

### 🧪 Chaos Engineering Framework
| Failure Mode | Severity | Response | RTO | RPO |
| :--- | :--- | :--- | :--- | :--- |
| MT5 Disconnect | High | Switch to backup, or halt | 30s | 0 |
| Network Split | Critical | Partition handling, quorum | 5s | 0 |
| Tick Delay > 5s | High | Reject orders, use last price | 10s | 0 |
| Database Failure | Critical | Automatic failover | 5s | 0 |

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR). This section details the cryptographic hashing of the audit trail (Merkle Chains) to provide undeniable proof of execution.*

### ⚖️ Institutional Audit Trail (V7.1.0)
Records: Why Trade? Why Now? Why Size? Why Confidence? Why Regime? Why Exposure?
- **Technical:** JSON/Avro, append-only WORM, SHA-256 hash chains, HSM-protected ECDSA signatures.
- **Retention:** 7 years minimum, S3 Glacier archival.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
**Compliance Matrix:**
- **MiFID III:** Pre-trade risk controls, kill switches, order-to-trade ratios.
- **Basel III FRTB:** Trading desk definition, backtesting, PLA tests.
- **GDPR:** Data classification, retention, deletion policies.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform. This ensures the project is adequately staffed and funded for long-term sustainability.*

### 👥 Minimum Viable Team (8 People)
1x Lead Architect, 2x Backend, 1x Quant Dev, 1x DevOps, 1x QA, 1x Risk/Compliance, 1x Operations.

### 📈 Economics & Revenue (V7.1.0)
- **Monthly Burn:** $42,700 - $66,600 (Phase 1).
- **Breakeven:** $5M - $7M AUM at 1% management fee.
- **Prop Target:** $1M - $2M capital requires 60-80% annual return.

---

## 🗺️ 11. Strategic Roadmap & Phase Progression
*The chronological plan for the project's evolution. It provides a clear path from the initial MVP to a fully scaled, multi-asset institutional trading platform.*

### 📍 Phase 1: MVP — Single Strategy (Months 0-6)
- Core Logic Proof on MT5, 7-Layer Risk Stack, Modular Monolith.
- **Kill Criterion:** If Sharpe < 0.5 in 6 months live, pivot or abandon.

### 🚀 Phase 2: Institutional Core (Months 6-12)
- FIX Gateway, Model Governance Engine, Exposure Graph.

### 🌐 Phase 3: Scale & Intelligence (Months 12-18)
- Multi-asset, FinCon Terminal dashboard, full compliance certification.

### 🏛️ Phase 4: The Sovereign Platform (Months 18-24)
- Prime Brokerage (Goldman/Citi), Regulatory licenses (SEC/FCA/NFA).
### 🧱 The 10-Layer Institutional Stack
1. **Layer 0: Data Quality Firewall** (Z-Score validation, gap detection).
2. **Layer 1: Market Data Layer** (Binary MsgPack / Protobuf).
3. **Layer 2: Liquidity/Toxicity Intel** (VPIN / Order Flow Toxicity).
4. **Layer 3: Strategy Layer** (XGBoost + LSTM Ensemble).
5. **Layer 4: Portfolio Construction** (Dynamic Allocation & Netting).
6. **Layer 5: Risk Engine** (7-Layer Stack + Exposure Graph).
7. **Layer 5.5: Model Governance** (PSI Monitoring & Shadow Mode).
8. **Layer 6: Execution Intelligence** (Almgren-Chriss Optimal Liquidation).
9. **Layer 7: Broker Mesh** (Universal Abstraction for FIX/MT5/cTrader).
10. **Layer 8: Autonomous Recovery** (Self-healing & Dead-Man Switch).
11. **Layer 9: Audit & Explainability** (Merkle-Chained Provenance).

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation. This section ensures that all trading models are statistically sound and have a high probability of success in live markets.*

### 🧠 The Strategy Layer (XGBoost + LSTM Ensemble)
The core logic utilizes an ensemble of gradient-boosted trees and long short-term memory networks to identify probabilistic edges in market data.

### 🔬 The Phoenix Gauntlet (Model Governance)
Mandatory validation pipeline for the revamp:
**Research → Backtest → Chaos Stress → Walk Forward → Incubation → Shadow Trading → Production.**

### 📊 Statistical Verification Gates
- **Deflated Sharpe > 1.5** (Adjusted for selection bias).
- **White Reality Check p-value < 0.01** (10k bootstrap iterations).
- **PBO < 0.05** (Probability of Backtest Overfitting).

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section of the blueprint. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches (Levels 1-4). This is the 'Shield' of the sovereign engine.*

### 🛡️ The 7-Layer Risk Stack
The system enforces a strict 7-layer risk stack with explicit precedence to ensure capital preservation under all market conditions.

### 🛑 Kill Switch Protocols
Implement Level 1-4 automatic Kill Switch triggers based on drawdown, latency, or connectivity loss.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers. This includes FIX protocol implementation, slippage analytics, and the Almgren-Chriss model for optimal order execution. It ensures the system minimizes transaction costs.*

- **Layer 6: Execution Intelligence** (Almgren-Chriss Optimal Liquidation).
- **Layer 7: Broker Mesh** (Universal Abstraction for FIX/MT5/cTrader).
- **Slippage Analytics:** Real-time monitoring of B-book conflict detection and execution quality.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure. This includes the 'Dead-Man Switch', autonomous recovery procedures, and the use of chaos engineering to proactively identify weaknesses.*

- **Layer 8: Autonomous Recovery:** Self-healing and Dead-Man Switch.
- **Chaos Engineering:** Weekly "Game Days" to test system resilience under simulated failure modes.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR). This section details the cryptographic hashing of the audit trail (Merkle Chains) to provide undeniable proof of execution.*

- **Layer 9: Audit & Explainability** (Merkle-Chained Provenance).
- **Compliance Matrix:** MiFID III Pre-trade controls, Basel III FRTB reporting, GDPR data retention.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform. This ensures the project is adequately staffed and funded for long-term sustainability.*

### 👥 Team Structure (8-Person MVP)
- 1× Lead Architect, 2× Backend Engineers, 1× Quant Dev, 1× DevOps/SRE, 1× QA/Chaos, 1× Risk/Compliance, 1× Ops Manager.

### 📈 Economics (Phase 1)
- **Monthly Burn:** $42,700 - $66,600.
- **Breakeven:** $5M - $7M AUM at 1% management fee.

---

## 🗺️ 11. Strategic Roadmap & Phase Progression
*The chronological plan for the project's evolution. It provides a clear path from the initial MVP to a fully scaled, multi-asset institutional trading platform.*

### 📍 Phase 1: MVP & Logic Proof (Months 0-6)
- Core Logic Proof on MT5, 7-Layer Risk Stack, Modular Monolith.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- FIX Gateway, Model Governance Engine, Cost Attribution.

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- FinCon Terminal, Full Audit certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- Prime Brokerage, Multi-asset expansion.

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
*A table of potential risks, their probability, impact, and pre-defined mitigation strategies. This section is designed to anticipate and neutralize threats before they manifest.*

### 🚨 Existential Risks & Kill Criteria (V7.1.0)
- **Broker Bankruptcy:** Multi-broker mesh, regulated only.
- **MQL5 Dependency:** Primary FIX Gateway + MT5 Fallback.
- **Kill Criteria:** Terminate if DD > 15% in 30 days or no 8-person team in 12 months.

### 🚨 Devil's Advocate Deep Dive (Integration V1.1)
| New Risk Identified | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **MQL5 Dependency** | High | Severe | Primary FIX Gateway + MT5 Fallback. |
| **Adversarial Broker** | High | Severe | A-book/B-book monitoring + Conflict Detection. |
| **Regulatory Non-Compliance** | Medium | Catastrophic | Compliance-first audit hashing + MiFID III controls. |

---

## 📜 13. Appendices & Data Dictionary

### Appendix A: Regulatory Compliance Matrix (V7.1.0)
| Regulation | Jurisdiction | Requirement | Phase |
| :--- | :--- | :--- | :--- |
| **MiFID III** | EU | Pre-trade controls, Kill Switches | 2 |
| **Basel III FRTB** | Global | Backtesting, PLA tests | 3 |
| **GDPR** | EU | Data retention, Right to deletion | 1 |

### Appendix B: Technology Stack (V7.1.0)
- **API:** FastAPI | **DB:** PostgreSQL, QuestDB | **Cache:** Redis Cluster
- **ML:** XGBoost, PyTorch | **Inference:** ONNX Runtime
- **Infra:** Terraform, Pulumi, Kubernetes (Phase 2)

### Appendix C: Glossary
- **A-book/B-book:** Broker routing/conflict model.
- **CSCV/PBO:** Overfitting metrics.
- **WORM:** Write Once Read Many (immutable storage).
*A repository for technical details, regulatory matrices, and definitions of terms used throughout the document. It provides the granular data necessary for implementation.*

*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
