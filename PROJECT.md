# 🪐 Project Phoenix: Sovereign Execution Engine (V1.9)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.9 (Ruthless Pragmatism)
**Focus:** Working Core over Architectural Vanity.

✅ **Production Stable Core (Prioritized)**
✅ **Institutional Governance Layer (Strengthened)**
✅ **Adaptive Multi-Asset Foundation**
🔄 **Research & HA Extensions (Phased, Validated)**

⚠️ **CRITICAL NOTE:** V1.9 represents a fundamental realignment around **Ruthless Pragmatism**. We prioritize a "Working Core" over "Comprehensive Features". Architectural elegance is secondary to operational survivability and capital preservation.

✅ **Core Integrity:** Modular Monolith / Microkernel Architecture.
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf) + Event Sourcing.
✅ **Standard:** L99-Standard V2 Certified Framework.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (In-Progress).

### 🧐 Institutional Reality Audit (V1.9)
1.  **Targets are Tiered:** We replace fixed elitist targets with tiered milestones to prevent forced overfitting.
2.  **Architecture is Pragmatic:** Use Python + FastAPI for the core; offload hot paths to C++/Rust only if latency benchmarks fail.
3.  **Liquidity is Hybrid:** Recognizing that true liquidity is opaque, we use observed L2 data plus proxies (Spread dynamics, COT reports, Volume profiles).
4.  **Validation is Automated:** Economic rationale checks and strict gates for all features before promotion.

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** Democratize institutional-grade algorithmic trading via transparent, auditable, resilient systems prioritizing **capital preservation** and verifiable statistical edge over speculative prediction.

**Mission:** Maximize long-term risk-adjusted expectancy through discipline. Targets are aspirational milestones, not guarantees. Start conservative.

### 📊 Performance Mandates (Tiered Milestones)
| Metric | Phase 1 Target | Stretch Target | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **Max Drawdown** | < 15.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | **CRITICAL** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Values (Pragmatic Realignment)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Pragmatic Execution:** Deliver a working core before chasing perfection.
- **Simplicity Budget:** Every subsystem must justify its operational burden: `(Alpha + Risk Reduction) < (Maintenance Cost + Failure Surface)`.
- **Probabilistic Regime Awareness:** Scale risk continuously based on ensemble confidence.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 Architecture (V7.1 Phoenix Core Refinement)
Event-Driven Microkernel with **pragmatic HA**. Prioritize simplicity and testability.
- **Sovereign Ingress:** AES-256 + rate limiting, broker-agnostic adapters.
- **DataHub HA:** Primary + Secondary + immutable Event Journal (Event Sourcing + CQRS). Snapshots for fast recovery.
- **Event Bus:** Standardized, acyclic (resolved circular deps via explicit contracts).
- **Hot Paths:** Profiled; offload to C++/Rust extensions if Python latency exceeds targets.
- **Persistence:** PostgreSQL for governance + QuestDB for telemetry + S3-compatible storage for snapshots.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Structural Market Intelligence (V1.9 Refinement)
- **Liquidity Proxies:** In addition to L2 data, use spread dynamics, COT reports, and order flow signatures.
- **Ensemble Diversity:** Prioritize ensembles of diverse models over single complex learners.
- **Explainability:** Integrate SHAP/LIME to understand model attribution.
- **MLOps:** Use MLflow or similar for drift tracking and experiment management.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V2+
- **Exposure Graph:** Use Graph DB (NetworkX/Neo4j) to map complex currency correlations and factor exposures.
- **Kill Switches:** Expanded to include **Hedge** and **Reduce** actions in addition to Liquidation.
- **Broker Health:** Scoring with backtested weights and automatic failover prototype.
- **Pre-trade Sandbox:** All orders must pass a Monte Carlo simulation in a synthetic sandbox before submission.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Liquidity & Multi-Broker (V1.9)
- **Dual-Broker Failover:** Start with dual-broker setup; expand to multi-broker only after stability is proven.
- **Cost Attribution Engine:** Mandatory tracking of all execution costs (Slippage, Spread, Commission, Latency) per strategy.

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure.*

- **Full Replay Testing:** Mandatory replay of event journals to verify state reconstruction.
- **Chaos Simulations:** Phased approach, starting with simulation before live injection.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

- **Enhanced Provenance:** Decision Provenance Graphs showing exactly which model/feature triggered which trade.
- **Compliance first:** Build audit trails for MiFID III and Basel FRTB from day 1.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform.*

### 👥 Minimum Viable Team (V1.9 Expanded)
- 1x Lead Architect
- 2x Backend Engineers (Python/Rust)
- 1x Quant Dev
- 1x **Ops Engineer** (Monitoring, Chaos, On-call)
- 1x QA/SDET
- 1x Risk/Compliance
- 1x Operations Manager

**Rituals:** Post-trade review rituals and obsessive decision provenance documentation are mandatory.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V1.9 Prioritized)
*The chronological plan for the project's evolution. MVP = Core risk + execution + basic governance.*

### 📍 Phase 1: Rock-Solid Core (Immediate)
- [x] Resolve EventBus dependencies, standardize security.
- [ ] Implement Model Governance basics + drift tracking.
- [ ] DataHub HA + Event Journal + snapshots.
- [ ] Exposure Graph + basic 7-layer risk stack.
- [ ] Automated validation pipeline (backtest → shadow).
- [ ] Chaos simulations + kill switch testing.

### 🚀 Phase 2: Intelligence & Execution
- Execution Analytics, Broker Health scoring, Macro scaling.
- Liquidity proxies + regime engine.
- ONNX standardization for all ensembles.

### 🌐 Phase 3: Scale & Polish
- FinCon Terminal (Iterative, start with Grafana).
- Full L99 automation.
- Multi-broker orchestration (after single/dual proven).

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Forced Overfitting** | High | Severe | Tiered milestones + Walk-forward validation. |
| **Architecture Death** | Medium | Severe | **Simplicity Budget** + Ruthless prioritization. |
| **MQL5 Dependency** | High | Severe | FIX Gateway migration (Phase 2). |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
