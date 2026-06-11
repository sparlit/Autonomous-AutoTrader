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
