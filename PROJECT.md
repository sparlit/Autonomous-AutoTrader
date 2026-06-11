# 🪐 Project Phoenix: Sovereign Execution Engine (V1.14)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.14 (Multi-Asset V2 Alignment)
**Focus:** Institutional Regime-Aware Portfolio Trading & Multi-Asset Autonomy.

✅ **Architecture Design:** (Completed V2.0)
✅ **Risk & Portfolio Framework:** (Completed)
✅ **Consensus & Execution Framework:** (Completed)
🔄 **Multi-Asset Autonomy:** (FX, Metals, Indices, Oil, Crypto, CFDs)
🔄 **Multi-Terminal Management:** (Active Implementation)

⚠️ **CRITICAL NOTE:** V1.14 integrates the **V2.0 Autonomous Multi-Asset AI Platform** specification. We strictly enforce the **Accepted Architecture**: `Market State → Risk State → Opportunity State → Portfolio Impact → Capital Allocation → Execution`.

✅ **Core Integrity:** Modular Monolith / Hybrid (Python Brain + MT5 Execution).
✅ **Governance:** PostgreSQL (TimescaleDB) + Redis (Hot Cache).
✅ **Standard:** L99-Standard V3 / Institutional V2 Certified.
🟡 **Hardening:** Implementation of 15-Layer Institutional Stack (Active).

---

## 👁️ 2. Vision, Mission & Strategic Mandates
*The Vision and Mission provide the philosophical foundation of the project. This section also outlines the 'Strategic Mandates'—the non-negotiable performance metrics and risk boundaries.*

**Vision:** Democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy (EV Optimization) while maintaining strict capital preservation through institutional-grade governance.

### 📊 Performance Mandates (V2.0 Benchmarks)
| Metric | Primary Target | Stretch Target | Priority |
| :--- | :--- | :--- | :--- |
| **Expected Value (EV)** | > Threshold | Maximized | **ABSOLUTE** |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 0.1% | < 0.01% | **ABSOLUTE** |
| **Execution Latency** | < 100µs | Optimized | Critical |

---

## 📐 3. Operational Philosophy & Governance Principles
*This section codifies the 'Divine Laws' of the system. It includes the Simplicity Budget, the Edge Attribution Framework, and the Stability Paradox Resolution.*

### 💎 Core Principles (V2.0)
- **Capital Preservation First:** Risk before reward in every deployment.
- **Regime-Based Trading:** Strategies are activated/weighted based on detected Market State.
- **Portfolio First:** No trade may violate global portfolio correlation or exposure limits.
- **Probabilistic Decision Making:** Replacing binary logic with ensemble consensus and EV forecasting.
- **Final Authority:** The **Risk Engine** is the final authority. No AI model, strategy, or dashboard control may override it.

### 🧠 Cognitive Decision Heuristics (Integration V1.3)
- **Uncertainty over Prediction:** Ask "does this setup have positive expectancy?"
- **Invalidation-First Thinking:** Every thesis begins with "Where is this wrong?"

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🧱 The 15-Layer Institutional Stack (V2.0 Expansion)
- **Layer 1: Market Data Engine** (Tick ingestion, MICROSTRUCTURE analysis).
- **Layer 2: Feature Engineering** (Momentum, Volatility, Cointegration, Sentiment).
- **Layer 3: Market Regime Classifier** (Trending, Ranging, Volatile, Crisis, News).
- **Layer 4: Risk Classification Engine** (Low, Medium, High, Extreme).
- **Layer 5: Opportunity Quality Engine** (A+ to D scoring based on EV/Impact).
- **Layer 6: Portfolio Management** (Currency/Asset/Sector Exposure Matrices).
- **Layer 7: News & Sentiment** (FinBERT, Central Bank Tone, Importance Classifier).
- **Layer 8: AI Decision Support** (Risk forecasting, EV distribution, Drift detection).
- **Layer 9: Strategy Router** (Activates strategy groups per regime).
- **Layer 10: Dynamic Consensus** (Regime-based weighted strategy ensemble).
- **Layer 11: Position Sizing** (3-Tier: Fixed -> Dynamic -> Advanced).
- **Layer 12: Pyramiding Engine** (Scaling, Profit Locking, max 4 layers).
- **Layer 13: Execution Engine** (Order validation, Retry logic, Broker compatibility).
- **Layer 14: Monitoring Engine** (System/Model/Risk health).
- **Layer 15: Dashboard Engine** (Executive/Trading/Research visualization).

### 🧱 Platform Responsibilities
- **MT5 (Execution Platform):** Data collection, Order execution, Position tracking, Dashboard displays, Emergency controls.
- **Python (Decision Platform):** All Intelligence (Market Engine, Feature, Regime, Risk, AI, Strategy, Execution Queue).

### 🧱 Technical Specifications (V1.14 Unified)
- **Kernel:** Rust-Python Hybrid (V1.12 Integration).
- **Database:** PostgreSQL + TimescaleDB (Relational/TS) + Redis (Live Cache).
- **Security:** AES-256-GCM + SHA-384 HMAC + JWT RBAC.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 🧠 Strategy Library (V2.0)
- **Trend Following:** EMA/SMA Cross, Donchian, Ichimoku, SuperTrend.
- **Mean Reversion:** Bollinger, Cointegration Pairs, Williams %R, MA Spread.
- **Volatility Expansion:** ATR Expansion, Opening Range Breakout, VWAP Breakout.
- **High Speed Execution:** Tick Velocity, Spread Dynamics, Order Flow Approximation.
- **AI Enhanced:** XGBoost, Random Forest, LSTM, Meta Ensemble.

### 🧠 Dynamic Consensus Engine
- **No Static Weights:** Strategy influence changes dynamically per regime (e.g., Trend 0.70 in Trending, 0.05 in Range).
- **Expectancy Engine:** EV = (Pwin × AvgWin) / (Ploss × AvgLoss). EV must exceed threshold for trade approval.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ Institutional Risk Architecture V2
- **The Risk Budget Tree:** Account -> Monthly -> Weekly -> Daily -> Trade.
- **Hard Risk Limits:**
  - **Risk Per Trade:** 0.01%.
  - **Risk Per Symbol:** 0.10%.
  - **Daily Risk Budget:** 1.00%.
- **Exposure Management:** Currency, Asset, Sector, Factor, and Correlation exposure enforcement.

### 🛡️ Position Sizing & Pyramiding (V2.0)
- **Tier 1:** Fixed Base 0.01 Lots (Safety Baseline).
- **Tier 2:** Dynamic Scaling (Volatility, Equity, Portfolio Heat).
- **Pyramiding:** Max 4 layers; requires Break Even active and Trend confirmation for Layer 2+.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Multi-Terminal & Broker Mesh
- **Multi-Terminal:** Support for multiple MT5 instances, brokers, and accounts.
- **Broker Compatibility Layer:** Standardizes symbol mapping, margin rules, and execution constraints across counterparties.
- **Execution Intelligence:** Order Flow Toxicity (VPIN) and Microstructure Jitter analysis (V1.12 Integration).

---

## 🛠️ 8. Operational Resilience & Self-Healing
*Defines the system's ability to maintain operations in the face of infrastructure failure.*

### 🛑 Circuit Breakers & Safety Systems
- **Global Kill Switch:** Panic Button for immediate liquidation/flattening.
- **Technical Breakers:** MT5/Broker disconnect, Liquidity collapse, Spread explosion.
- **Flash Crash Protection:** Automated halt and protection of winning trades.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

- **L99 Certification Framework V2:** Independent passing of Code, Infra, Risk, Exec, Research, and Resilience certifications.
- **Audit Trail:** Decision Provenance records *Why Trade? Why Size? Why Stop?* etc.

---

## 👥 10. Human Capital & Economic Model
*Outlines the team structure and financial resources required to build and maintain the platform.*

### 👥 Dashboard Architecture (V2.0)
- **Executive Dashboard:** Balance, Equity, DD, Global Risk.
- **Trading Dashboard:** Regime, Consensus, Signals, Pyramids.
- **Research Dashboard:** Model Health, Drift, Feature Importance.

---

## 🗺️ 11. Strategic Roadmap & Development Priority
*The chronological plan for the project's evolution. MVP = Core risk + execution + basic governance.*

1. **Priority 1:** Market Data Engine & Infrastructure.
2. **Priority 2:** Regime Engine & Risk Engine (Final Authority).
3. **Priority 3:** Portfolio & Execution Engines.
4. **Priority 4:** Strategy Library & Consensus Layer.
5. **Priority 5:** AI, News/Sentiment, and Dashboard integration.

---

## ⚠️ 12. Risk Assessment & Failure Modes (The Pre-Mortem)
| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Architecture Death** | Medium | Severe | **Accepted Architecture** Filter sequence. |
| **Regime Mis-ID** | High | Severe | **Dynamic Consensus** + Multi-TF Analysis. |
| **Flash Crash** | Low | Catastrophic | **Global Kill Switch** + Safety Systems. |

---

## 📜 13. Appendices & Data Dictionary
- **MT5 Dashboard:** Real-time visualization of Risk Score, Strategy Status, and Pyramiding status.
- **Asset Classes:** Forex, Metals, Indices, Oil, Crypto, CFDs.

*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
