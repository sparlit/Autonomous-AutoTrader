# 🪐 Project Phoenix: Sovereign Execution Engine (V1.11)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.11 (Technical Protocol Hardening)
**Focus:** Granular Autonomous Execution & Risk Protocols.

✅ **Production Stable Core (Prioritized)**
✅ **Multi-Symbol Architecture (Implemented)**
🔄 **Autonomous Risk Layer (Under Refinement)**
🔄 **Adaptive Multi-Asset Foundation**

⚠️ **CRITICAL NOTE:** V1.11 formalizes the **Phase 1 Implementation Protocol** for the MQL5 autotrader core. We prioritize a "Working Core" with hard-coded risk parameters (2% daily limit, 1% per-trade risk) to ensure survival in retail FX environments.

✅ **Core Integrity:** Modular Monolith / MQL5 Hybrid.
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf) + Event Sourcing.
✅ **Standard:** L99-Standard V2 Certified Framework.
🟡 **Hardening:** Implementation of 12-Layer Institutional Stack (In-Progress).

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** Democratize institutional-grade algorithmic trading via transparent, auditable, resilient systems prioritizing **capital preservation** and verifiable statistical edge over speculative prediction.

**Mission:** Maximize long-term risk-adjusted expectancy (Target 5-10% Monthly) through discipline. Targets are aspirational milestones, not guarantees. Start conservative.

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

### 🧱 Phase 1 Execution Mechanics (MQL5 Protocol)
The Phase 1 core utilizes an **Autonomous Multi-Symbol Autotrader** architecture:
- **SymbolContext Extension:** Every symbol maintains a localized state including `atrValue`, `signalLong/Short`, and `lastSignalTime` (1-hour signal cooldown).
- **Portfolio-Level Risk:** Global enforcement of a **2% Maximum Daily Loss Limit** (`MaxDailyLossPercent`) managed via `RiskManagement.mqh`.
- **Automated Sizing:** Lot sizes are dynamically calculated based on **1% per-trade risk** of Account Equity and ATR-derived Stop Loss distance.
- **Volatility Scaling:** ATR(14) on H1 timeframe determines:
  - **Stop Loss:** 1.5x ATR distance from entry.
  - **Take Profit:** 3.0x ATR distance (2:1 R/R ratio).
  - **Trailing Stop:** 1.0x ATR distance, trailing only in profit.

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
- **Portfolio Risk:** Hard lock on `dailyPnL` breching 2% of `dailyStartEquity`.
- **Symbol Risk:** ATR-based volatility freeze if spreads or tick latency exceed thresholds.
- **Infrastructure Risk:** Safe-Mode disconnect on `heartbeat` failure.
- **Broker Health:** Scoring with backtested weights and automatic failover prototype.
- **Pre-trade Sandbox:** All orders must pass a Monte Carlo simulation.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Autonomous Execution (V1.11 Protocol)
- **Signal Logic:** Standardized MA Crossover (Fast: 9, Slow: 21) on H1 timeframe as baseline signal.
- **Execution Logic:** `OpenTrade()` uses `magicBase` per symbol for independent tracking.
- **Position Reconciliation:** `ManagePositions()` runs every tick to update SL/TP and enforce time-based exits.
- **Zombie Control:** Mandatory position closure after **24 hours** to prevent long-term exposure drift.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V1.11 Implementation)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Rock-Solid Core (Immediate)
- [x] Resolve EventBus dependencies, standardize security.
- [ ] **Task 1-5:** Risk Management foundations and SymbolContext extension.
- [ ] **Task 6-10:** Automation logic (Lot sizing, ATR scaling, Position Management).
- [ ] **Task 11-12:** Dashboard enhancement and full Strategy Tester validation.

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
