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
