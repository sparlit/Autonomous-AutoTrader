# Project Phoenix Revamp TODO - V1.13 (V7.0.0 Alignment)

## Epic 1 — Core Institutional Governance
- [ ] Implement **Layer 5.5: Model Governance Engine** (PSI, Feature Drift, Shadow Mode).
- [ ] Deploy **Confidence Decay** logic for aging models.
- [ ] Finalize **DataHub HA Architecture** with RAID-class Event Journaling.
- [ ] Resolve EventBus circular dependencies in hybrid kernel.

## Epic 2 — Data Integrity & Intelligence
- [ ] Implement **Layer 0: Data Quality Firewall** (Tick/Gap/Spread validation).
- [ ] Integrate **Macro Intelligence Layer** (Deterministic risk reduction).
- [ ] Automate **Wyckoff Phase Detection** and FAISS Signature Retrieval.
- [ ] Deploy **Alpha Validation Engine** for incremental MAR checks.

## Epic 3 — Risk & Portfolio Construction
- [ ] Implement **Exposure Graph Engine** (Net currency exposure limits).
- [ ] Deploy **7-Layer Risk Stack** with hard-coded veto logic.
- [ ] Build **Pre-trade Monte Carlo Sandbox** (100k runs).
- [ ] Implement **Kill Switch Hierarchy** (Strategy -> Global -> Safe Mode).

## Epic 4 — Execution & Broker Health
- [ ] Implement **Broker Health Engine** (Continuous quality scoring).
- [ ] Build **Execution Analytics Engine** (Fill rate, Slippage, Latency).
- [ ] Transition to **FIX 4.4/5.0 Gateway** priority.

## Epic 5 — Operations & Resilience
- [ ] Automate **Chaos Engineering Framework** (MT5 disconnect, Network split).
- [ ] Launch **FinCon Terminal** (React/Next.js "Audit Explorer").
- [ ] Establish **Decision Provenance Graphs** in Audit Trail.

## Epic 6 — Production Readiness (L99 V2)
- [ ] L99-A: Code Integrity | L99-B: HA Reliability.
- [ ] L99-C: Risk Management | L99-D: Execution Quality.
- [ ] L99-E: Research Validation | L99-F: Resilience.
# Project Phoenix Revamp TODO - V1.10 (Autonomous Implementation)

## Epic 1 — MQL5 Autonomous Implementation
- [ ] **Task 1:** Extend SymbolContext structure in `Symbols.mqh` with `dailyPnL`, `lotSize`, `stopLoss`, `atrValue`, and signal flags.
- [ ] **Task 2:** Add global risk variables in `AutoTraderPro.mq5` (`dailyStartEquity`, `tradingEnabled`).
- [ ] **Task 3:** Initialize daily loss tracking in `OnInit()`.
- [ ] **Task 4:** Create `RiskManagement.mqh` with `ResetDailyLossIfNeeded()` and `CheckDailyLossLimit()` (2% cap).
- [ ] **Task 5:** Integrate daily loss checks into `OnTick()` loop.
- [ ] **Task 6:** Implement `CalculateLotSize()` using fixed 1% risk of equity.
- [ ] **Task 7:** Implement `CalculateATRAndLevels()` for SL (1.5x) and TP (3.0x).
- [ ] **Task 8:** Refactor `AnalyzeAndTrade()` for full autonomous signal execution and position management.
- [ ] **Task 9:** Update `OpenTrade()` to use `ctx->magicBase`.
- [ ] **Task 10:** Implement ATR-based Trailing Stops and 24-hour time exits in `ManagePositions()`.

## Epic 2 — Foundation & Core Integrity
- [x] Audit EventBus circular dependencies; refactor to explicit contracts.
- [ ] Implement Event Sourcing (CQRS) with Snapshotting.
- [ ] Set up Docker/K8s dev/prod parity with Prometheus/Grafana.

## Epic 3 — Risk & Resilience Hardening
- [ ] Build Exposure Graph (Neo4j or NetworkX) for currency/factor correlations.
- [ ] Implement Pre-trade Monte Carlo Sandbox.
# Project Phoenix Revamp TODO - V1.9 (Ruthless Pragmatism)

## Epic 1 — Foundation & Core Integrity
- [x] Audit EventBus circular dependencies; refactor to explicit contracts.
- [ ] Profile Python/MQL5 bridge; offload hot paths to Rust if > 10ms.
- [ ] Implement Event Sourcing (CQRS) with Snapshotting.
- [ ] Set up Docker/K8s dev/prod parity with Prometheus/Grafana.

## Epic 2 — Model Governance & Intelligence
- [ ] Deploy drift detectors (PSI, Evidently) + shadow mode logic.
- [ ] Integrate Liquidity Proxies (Spread dynamics, COT, Volume).
- [ ] Build Alpha Validation Engine (Incremental MAR/Expectancy).
- [ ] Standardize ONNX for all ensemble models.

## Epic 3 — Risk & Resilience Hardening
- [ ] Build Exposure Graph (Neo4j or NetworkX) for currency/factor correlations.
- [ ] Implement Pre-trade Monte Carlo Sandbox.
- [ ] Expand Kill Switch actions (Hedge/Reduce) beyond liquidation.
- [ ] Deploy Chaos Suite (Latency injection, DB failover, clock skew).

## Epic 4 — Execution & Broker Health
- [ ] Implement Broker Health Scorer with backtested weights.
- [ ] Build dual-broker failover prototype.
- [ ] Deploy Cost Attribution Engine (Track all hidden costs per strategy).

## Epic 5 — Operations & Documentation
- [ ] Define on-call runbooks for live incident response.
- [ ] Document decision provenance graph schemas.
- [ ] Establish post-trade review rituals and audit logs.

## Epic 6 — Production Readiness (L99 V2)
- [ ] L99-A: Code Integrity (100% Risk/Exec coverage).
- [ ] L99-B: HA Reliability (Event replay verified).
- [ ] L99-C: Risk Management (MC Sandbox passed).
- [ ] L99-D: Execution Quality (Slippage < 1 pip).
- [ ] L99-E: Research Validation (OOS decay monitored).
- [ ] L99-F: Resilience (Chaos suite survived).

## Success Metrics
- Zero critical bugs in shadow trading for 1 month.
- Positive expectancy (> 0.5 Sharpe) in live shadow for 3 months.
- RTO < 30s for all core failures.
# 🛠️ Project Phoenix: Master TODO Tracker (V1.7 God-Tier Revamp)

## Epic 1 — Architectural Foundations & Security
- [x] Replace SQLite governance store with PostgreSQL
- [ ] Implement **AES-256-GCM** across all sovereign ingress/egress
- [ ] Transition from centralized Event Bus to **Domain Event Buses**
- [ ] Design event schema versioning and Buf Registry integration
- [ ] Implement snapshot and replay architecture for event sourcing

## Epic 2 — Data Integrity & Intelligence
- [ ] Implement **Layer 0: Data Quality Firewall** (Tick/Gap/Spread validation)
- [ ] Build **Probabilistic Regime State Machine** (HMM + GARCH ensemble)
- [ ] Deploy **Alpha Validation Engine** (Mandatory incremental value checks)
- [ ] Integrate Wyckoff and FAISS into Research Shadow Mode

## Epic 3 — Portfolio & Risk construction
- [ ] Implement **Layer 4: Portfolio Intelligence** (Correlation/Factor budgeting)
- [ ] Deploy **Kill Switch Decision Tree** (Liquidate/Reduce/Hedge/Freeze)
- [ ] Automate **Macro Action Matrix** (Deterministic risk scaling for events)
- [ ] Build Factor and Tail exposure tracking in Exposure Graph

## Epic 4 — Execution & Broker Mesh
- [ ] Transition to **FIX 4.4/5.0 Gateway** priority
- [ ] Implement **Broker Mesh** (Primary/Secondary/Tertiary failover)
- [ ] Deploy **Cost Attribution Engine** (Slippage/Latency/Spread per strategy)
- [ ] Build Capacity Analysis (Market Impact monitoring)

## Epic 5 — Governance & Explainability
- [ ] Implement **Layer 5.6: Meta-Governance** (Monitor Drift Detector accuracy)
- [ ] Build **Decision Provenance Graphs** for full explainability
- [ ] Launch **FinCon Terminal** (React/Next.js "Audit Explorer")
- [ ] Automate Confidence Calibration monitoring

## Epic 6 — Resilience & Recovery
- [ ] Implement **Layer 8: Autonomous Recovery Engine**
- [ ] Automate Root Cause Analysis for system failures
- [ ] Standardize daily Chaos Engineering "Game Days"
- [ ] Finalize Recovery Verification workflows

## Epic 7 — Production Readiness (L99 V2)
- [ ] L99-A: Code Integrity (100% Risk Engine Coverage)
- [ ] L99-B: Infrastructure Reliability (HA failover < 5s)
- [ ] L99-C: Risk Management (Zero uncontrolled DD > 2%)
- [ ] L99-D: Execution Quality (Slippage < 1 pip)
- [ ] L99-E: Research Validation (White Reality Check passed)
- [ ] L99-F: Resilience & Recovery (1000 Chaos survived)
# 🛠️ Project Phoenix: Master TODO Tracker (V1.6 Realignment)

## Epic 1 — Architectural Foundations
- [ ] Replace SQLite governance store with PostgreSQL
- [ ] Design event schema versioning
- [ ] Implement snapshot architecture
- [ ] Implement replay architecture
- [ ] Implement event compaction
- [ ] Remove centralized bus bottlenecks
- [ ] Introduce domain buses

## Epic 2 — Data Integrity
- [ ] Tick validation
- [ ] Duplicate detection
- [ ] Timestamp verification
- [ ] Spread anomaly detection
- [ ] Data lineage tracking
- [ ] Data quality scoring
- [ ] Data quality firewall

## Epic 3 — Portfolio Intelligence
- [ ] Correlation engine
- [ ] Factor exposure engine
- [ ] Portfolio optimizer
- [ ] Capital allocator
- [ ] Risk budgeting
- [ ] Dynamic rebalancer

## Epic 4 — Governance
- [ ] Drift detection
- [ ] Governance calibration
- [ ] Confidence calibration
- [ ] Meta-governance engine
- [ ] Governance audit framework

## Epic 5 — AI Validation
- [ ] Alpha attribution engine
- [ ] Incremental value analysis
- [ ] Model contribution scoring
- [ ] Shadow validation framework
- [ ] Model retirement engine

## Epic 6 — Execution Intelligence
- [ ] Execution simulator
- [ ] Slippage modeling
- [ ] Fill probability model
- [ ] Broker quality engine
- [ ] Broker mesh failover

## Epic 7 — Resilience
- [ ] Autonomous recovery engine
- [ ] Self-healing workflows
- [ ] Chaos engineering automation
- [ ] Disaster recovery testing
- [ ] Recovery certification

## Epic 8 — Research
- [ ] Walk-forward automation
- [ ] Monte Carlo engine
- [ ] White Reality Check
- [ ] PBO engine
- [ ] Capacity analysis
- [ ] Execution realism testing

## Epic 9 — Explainability
- [ ] Decision graph engine
- [ ] Risk attribution engine
- [ ] Model attribution engine
- [ ] Execution attribution engine
- [ ] Audit explorer

## Epic 10 — Production Readiness
- [ ] L99-A Certification
- [ ] L99-B Certification
- [ ] L99-C Certification
- [ ] L99-D Certification
- [ ] L99-E Certification
- [ ] L99-F Certification
- [ ] Full platform certification
