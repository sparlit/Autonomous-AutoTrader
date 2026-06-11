# Project Phoenix Revamp TODO - V1.24 (Hardened Thresholds)

## Epic 1 — High-Precision Resilience
- [ ] Implement **RTO < 5s** failover for MT5 Disconnect scenarios.
- [ ] Configure **RPO = 0** event journaling for the risk path.
- [ ] Automate **Position Reconciliation** (30s frequency) with broker-side APIs.
- [ ] Build **Phantom Position Handler** for internal-to-broker divergence.

## Epic 2 — Statistical Verification Engine
- [ ] Automate **10,000 bootstrap iterations** for White Reality Check.
- [ ] Build **Deflated Sharpe Ratio** calculator with 2024 deflation factors.
- [ ] Implement **expanding window walk-forward** (10-fold) for all strategies.
- [ ] Integrate **half-Kelly sizing** constraints into the Sizing Engine.

## Epic 3 — Broker & Market Impact
- [ ] Calibrate **Square-Root Market Impact** model for H1 major pairs.
- [ ] Implement **Adverse Selection Monitor** (Rejection rate vs. Profitability).
- [ ] Design **Broker Diversification** layer (Min 3 brokers connectivity).

## Epic 4 — Sovereign Hardening
- [ ] Finalize **L99-A/B/C/D/E/F** certifications with new hardened metrics.
- [ ] Deploy **RAFT consensus** (etcd/Consul) for kernel high-availability.

## Success Metrics
- P99 RTO < 5s for all critical infrastructure failures.
- Zero data loss (RPO=0) on risk-related events.
- 100% compliance with Hardened Statistical Verification Gates.
