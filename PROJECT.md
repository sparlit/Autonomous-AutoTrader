# 🌌 Project Autonomous AutoTrader (AAT)
**Internal Code-Name**: Phoenix Gauntlet
**Version**: V2.3.0-ASCENDANT

## 📖 1. Project Identity & Vision
AAT operates under a Zero-Tolerance Standard for stubs and placeholders.
AAT is a high-probability, autonomous trading system engineered for MetaTrader 5, powered by a Python-based "Brain." It operates on the principle of **Defensive Alpha**: capital preservation is the primary objective; profit is a secondary outcome of discipline.

### 💎 Core Values (V7.1.0)
- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Python + MT5:** Leveraging the best of both ecosystems.

---

## 🛠️ 2. System Overview (V1.5 Refinement)
The system is built as a microkernel with event-driven decoupling, transitioning from a single-chart instance to a **Coordinator/Agent** model.

### 🧩 Components
- **Python Hive (Coordinator):** Global risk management via **AES-256-GCM Secure Gateway**.
- **MQL5 Agents:** Ultra-slim execution units (MT5 Phase 1, FIX Protocol Priority Phase 2).
- **Persistence:** PostgreSQL, QuestDB, and Redis Cluster (Institutional) or SQLite (Local).
- **Protocol Buffers (Protobuf):** High-speed serialization for the **Event Bus**.

---

## 🧠 3. Quantitative Strategy
To resolve logic conflicts, AAT uses a hierarchical decision engine:

1. **Stage 1: Veto Filters (Sequential):** Hard checks.
2. **Stage 2: Strategy Voting (Consensus):** Weighted votes with |score| >= 0.7.

---

## 🏗️ 4. System Architecture
### 🧱 Technical Specifications
- Microkernel (plug-in) with event-driven decoupling.
- Zero side effects, hot-swappable modules.

### 🧠 ML Architecture
- HMM with GARCH regime detection.
- Context Loop vs Execution Loop.

---

## 🛡️ 6. Risk Management
### 🛡️ The 7-Layer Risk Stack
1. **L1: Infrastructure** - Heartbeat, Latency.
2. **L2: Global Risk** - Daily Loss, Drawdown.
3. **L3: Symbol Risk** - Spread, ATR.
4. **L4: Strategy Risk** - Cooldowns.
5. **Stage 5: Monte Carlo simulation** - Pre-trade validation.
6. **Conflict Resolution:** Higher precedence always wins.

---

## 👥 10. Minimum Viable Team (8 People)
- 1x Lead Architect
- 2x Backend/Kernel Engineers
- 1x Quant Dev
- 1x DevOps/SRE
- 1x QA/SDET
- 1x Risk/Compliance
- 1x Operations/Terminal Manager

---

## 🗺️ 11. Strategic Roadmap
### 📍 Phase 1: MVP (Months 0-6)
- [ ] Modular Monolith
- [ ] Kill Criterion: Sharpe < 0.5
- [ ] XGBoost/LSTM initial models.

### 🚀 Phase 2: Institutional (Months 6-12)
- [ ] FIX Gateway.

---

## ⚠️ 12. Risk Assessment
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **MQL5 Dependency** | High | Severe | FIX Gateway. |
| **Adversarial Broker** | High | Severe | Conflict Detection. |
| **Team Burnout** | Medium | High | 8-person redundancy. |

---

## 📜 13. Appendices
- Institutional Reality Audit: PostgreSQL mandatory for governance.
- SQLite is not for Audit.
