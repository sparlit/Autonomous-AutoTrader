# 🪐 Project Phoenix - AAT V7.5.0 (The Operational Sovereign)
## *The Institutional Trading Platform & Execution Engine*

### 🏛️ Status: The Global Revamp (Post-Autopsy)
Project Phoenix V7.5.0 represents a ground-up rebuild focused on **Operational Feasibility** over architectural vanity. We have pivoted from "Architectural Elegance" to **Survivability under Model Failure**.

✅ **Core Integrity:** Modular Monolith Architecture (MVP Stabilized)
✅ **Governance:** PostgreSQL (ACID) + Redis Streams (Protobuf)
✅ **Standard:** L99-Standard V2 Certified Framework
🟡 **Hardening:** Implementation of 10-Layer Institutional Stack (In-Progress)

---

## 👁️ 1. Vision & Mission

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient platform that prioritizes capital preservation, statistical validity, and operational survivability.

**Mission:** To maximize long-term risk-adjusted expectancy (Sortino > 3.0) through deterministic execution and mathematical discipline. We treat every trading signal as a probabilistic hypothesis that must survive an 11-stage gauntlet.

### 📊 Performance Mandates (Realistic & Phased)
| Metric | Phase 1 (Reality) | Phase 2 (Stretch) | Status |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.5 | Phase 1 |
| **Sortino Ratio** | > 1.5 | > 3.5 | Phase 1 |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Internal Latency** | < 100ms | < 100µs | Phase 2 Path |

---

## 📐 2. The Divine Governance Principles

To combat the **"Conspiracy of Complexity"** and false certainty, V7.5.0 enforces:

### A. The Simplicity Budget
Every subsystem must justify its operational burden. If **(Alpha + Risk Reduction) < (Maintenance Cost + Failure Surface)**, it is removed. We prioritize a "Working Core" over "Comprehensive Features."

### B. The Edge Attribution Framework
Every signal must prove its incremental value:
`Signal → Decision Change → Trade Outcome Change → Portfolio Alpha Improvement.`

### C. The Stability Paradox Resolution
Status checkmarks (`✅`) are strictly reserved for code that has passed L99-Standard verification. Aspirational goals stay in the roadmap.

---

## 🏗️ 3. Architecture: The Sovereign Trinity

Project Phoenix utilizes a **Modular Monolith** with clean boundaries, separating synchronous execution from asynchronous analytics.

### 🧩 System Overview
- **Sovereign Ingress:** AES-256-GCM Secure Gateway. MT5 (Phase 1 Bootstrap) → FIX 4.4/5.0 (Phase 2 Sovereign).
- **The Brain (Logic):** Python 3.11+ FastAPI Orchestrator using **Redis Streams** for exactly-once event processing.
- **Persistence Layer:** 
    - **PostgreSQL 15+:** ACID-compliant Audit Trail & Risk Config.
    - **QuestDB 7+:** High-frequency telemetry & Time-series.
    - **Redis Cluster:** Hot state, session data, and SPMC messaging.
- **Inference:** ONNX Runtime for INT8 quantized XGBoost + LSTM models.

---

## 🛡️ 4. The 10-Layer Institutional Stack

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

## 🔬 5. The Phoenix Gauntlet (Model Governance)

Mandatory validation pipeline for the revamp:
**Research → Backtest → Chaos Stress → Walk Forward → Incubation → Shadow Trading → Production.**

### Statistical Verification Gates
- **Deflated Sharpe > 1.5** (Adjusted for selection bias).
- **White Reality Check p-value < 0.01** (10k bootstrap iterations).
- **PBO < 0.05** (Probability of Backtest Overfitting).

---

## 👥 6. Team & Operational Growth

Project Phoenix mandates an **8-Person MVP Team** for 24/7 survivability:
- 1× Lead Architect (Project Manager)
- 2× Backend Engineers (Distributed Systems)
- 1× Quant Developer (Models & Research)
- 1× DevOps/SRE Engineer (K8s/Chaos)
- 1× QA/Chaos Engineer (Replay & Verification)
- 1× Risk & Compliance Officer (MiFID III/Basel)
- 1× Operations Manager (On-call/Incident)

---

## 🗺️ 7. Roadmap: The Sovereign Ascent (V7.5.0)

### 📍 Phase 1: MVP & Logic Proof (Months 0-6)
- [ ] Implement **Modular Monolith Core** on PostgreSQL/Redis.
- [ ] Build **7-Layer Risk Stack** with precedence enforcement.
- [ ] Prove logic on single-pair/single-broker MT5 implementation.
- [ ] **Kill Criterion:** If Sharpe < 0.5 after 6 months live, pivot or abandon.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- [ ] Implement **FIX 4.4/5.0 Gateway** (DMA path).
- [ ] Deploy **Model Governance Engine** with PSI drift detection.
- [ ] Implement **Cost Attribution Engine** (Spread/Slippage/Fee analysis).

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- [ ] Launch **FinCon Terminal** (React/Next.js dashboard).
- [ ] Full MiFID III/Basel FRTB audit compliance certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- [ ] Prime Broker integration and external capital on-boarding.
- [ ] Multi-asset expansion (Equities/Futures).

---

## 📈 8. Economics & Cost Model

**Estimated Monthly Burn (Phase 1):** $42,700 - $66,600
- **Team:** $40k - $60k (8 people)
- **Infra/Data:** $2.5k - $6k
- **Legal/Audit:** $2k - $5k

**Breakeven Requirement:** $5M - $7M AUM at 1% management fee (or equivalent proprietary return).

---

## ⚠️ 9. Failure Modes & Mitigations

| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Broker Bankruptcy** | High | Catastrophic | Multi-broker mesh + regulated only. |
| **Strategy Degradation** | High | Severe | Continuous monitoring + 4-Level Kill Switch. |
| **Regulatory Shutdown** | Medium | Catastrophic | Compliance-first audit hashing. |
| **Team Burnout** | Medium | Severe | Standardized documentation + 8-person redundancy. |
| **Data Corruption** | Low | Catastrophic | Merkle-anchored replay journal. |

---

## 📜 10. Appendices

### Appendix A: Regulatory Compliance Matrix
- **MiFID III:** Pre-trade risk controls and kill switches.
- **Basel III FRTB:** Trading desk definition and backtesting.
- **GDPR:** Data retention and portability.

---
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
