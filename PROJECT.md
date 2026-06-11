# 🪐 Project Phoenix: Sovereign Execution Engine (V1.10)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.10 (MQL5 Implementation Alignment)
**Focus:** Autonomous Multi-Symbol Execution & Portfolio Risk.

✅ **Production Stable Core (Prioritized)**
✅ **Multi-Symbol Architecture (Implemented)**
🔄 **Autonomous Risk Layer (Under Refinement)**
🔄 **Adaptive Multi-Asset Foundation**

⚠️ **CRITICAL NOTE:** V1.10 integrates the technical specifications for the **Autonomous Multi-Symbol Autotrader**. We prioritize a "Working Core" over architectural vanity, focusing on the 2% daily loss limit and automated execution mechanics.

✅ **Core Integrity:** Modular Monolith / MQL5 Hybrid.
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf) + Event Sourcing.
✅ **Standard:** L99-Standard V2 Certified Framework.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (In-Progress).

### 🧐 Institutional Reality Audit (V1.9)
1.  **Targets are Tiered:** We replace fixed elitist targets with tiered milestones.
2.  **Architecture is Pragmatic:** Use Python + FastAPI for core; MQL5 for localized symbol execution.
3.  **Liquidity is Hybrid:** Observed L2 data plus proxies.
4.  **Validation is Automated:** Economic rationale checks for all features.

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
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | **CRITICAL** |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Values (Pragmatic Realignment)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Pragmatic Execution:** Deliver a working core before chasing perfection.
- **Simplicity Budget:** Every subsystem must justify its operational burden.
- **Probabilistic Regime Awareness:** Scale risk continuously based on ensemble confidence.

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 Phase 1 Execution Mechanics (MQL5)
The Phase 1 core utilizes an **Autonomous Multi-Symbol Autotrader** architecture:
- **SymbolContext Extension:** Every symbol maintains a localized state including ATR volatility, signal state, and localized P&L.
- **Portfolio-Level Risk:** Global enforcement of a **2% Maximum Daily Loss Limit** before disabling new trades.
- **Automated Sizing:** Lot sizes are dynamically calculated based on 1% per-trade risk and ATR-derived Stop Loss distance.
- **Volatility Scaling:** ATR(14) on H1 timeframe determines Stop Loss (1.5x ATR) and Take Profit (3.0x ATR) to ensure a 2:1 Reward/Risk profile.

### 🧱 System Architecture (V7.1 Phoenix Core Refinement)
Event-Driven Microkernel with **pragmatic HA**.
- **Sovereign Ingress:** AES-256 + rate limiting, broker-agnostic adapters.
- **DataHub HA:** Primary + Secondary + Event Journaling.
- **Event Bus:** Standardized, acyclic Domain Event Buses.
- **Persistence:** PostgreSQL for governance + QuestDB for telemetry.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V2+
- **Exposure Graph:** Use Graph DB (NetworkX/Neo4j) to map complex currency correlations.
- **Kill Switches:**
  - **Level 1 (Portfolio):** 2% Daily Loss Limit (Hard disable for new entries).
  - **Level 2 (Symbol):** ATR-based volatility freeze.
  - **Level 3 (Infrastructure):** Safe-Mode disconnect.
- **Broker Health:** Scoring with backtested weights and automatic failover prototype.
- **Pre-trade Sandbox:** All orders must pass a Monte Carlo simulation.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Autonomous Execution (V1.10)
- **Symbol-Independent Analysis:** Each `SymbolContext` processes its own technical signals (MA Crossover, etc.) independently.
- **Centralized Position Manager:** Reconciles internal `SymbolContext` states with MT5 account positions every tick.
- **Trailing Stops:** ATR-based trailing logic (1.0x ATR distance) for favorable price movements.
- **Time-based Exit:** Mandatory position closure after 24 hours to prevent "Zombie Trades".

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V1.10 Implementation)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Rock-Solid Core (Immediate)
- [x] Resolve EventBus dependencies, standardize security.
- [ ] **Extend SymbolContext with Risk and Automation fields.**
- [ ] **Implement RiskManagement.mqh for portfolio-level loss limits.**
- [ ] **Deploy ATR-based SL/TP and Lot Sizing logic.**
- [ ] Automated validation pipeline (backtest → shadow).
- [ ] Chaos simulations + kill switch testing.

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Forced Overfitting** | High | Severe | Tiered milestones + Walk-forward validation. |
| **Broker Adverse Selection** | Medium | Catastrophic | Conflict detection + Broker mesh. |
| **Daily Limit Failure** | Low | Severe | **RiskManagement.mqh** global lock. |

---

## 📜 13. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
