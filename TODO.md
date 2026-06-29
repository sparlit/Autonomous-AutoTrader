# 📝 AAT V3.3.0 PENDING TASKS (TODO)

## 🔴 CRITICAL (System Stability)
- [ ] **Protobuf Migration**: Transition from JSON to Protocol Buffers for the event bus as mandated by Institutional Standards.
- [ ] **PostgreSQL Governance**: Implement PostgreSQL backend for Trade Ledger and Audit trail to support high-concurrency governance (replacing current SQLite implementation).
- [ ] **Kernel Compilation**: Verify 'aat_heavy' and 'aat_rust' kernels are fully optimized and linked for the target OS (Windows/Linux).

## 🟡 MAJOR (Feature Parity)
- [ ] **Complete 23-Brain Swarm**: Expand the current 18-brain cluster to the full 23-brain swarm by implementing remaining specialized ML and HMM brains.
- [ ] **Hardware Affinity Mapping**: Refine the 'HardwareAnalyst' to provide granular, cross-OS CPU affinity maps for optimal thread isolation.
- [ ] **FIX Protocol Phase 2**: Begin implementation of FIX protocol bridge for direct market access (DMA), bypassing MT5 for institutional speed.

## 🟢 MINOR (Maintenance & UX)
- [ ] **Web Dashboard JWT**: Finalize the JWT authentication layer for the FastAPI remote telemetry server.
- [ ] **MQL5 HUD Enhancement**: Add more granular Bayesian confidence intervals to the MT5 Canvas HUD overlay.
- [ ] **Automated Backtesting**: Integrate the 'ml_trainer.py' with the new parallel brain swarm for recursive strategy optimization.

---
**Status**: 85% Operational (Phoenix Gauntlet Active)
