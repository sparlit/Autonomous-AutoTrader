# 🛠️ Project Phoenix: Engineering TODO (V1.32 Edge Alignment)

> **Status:** Edge Persistence Complete
> **Focus:** MQL5 Database Validation & Rust Kernel

## 🗃️ Epic 0 — MQL5 Edge Persistence (COMPLETE)
- [x] Implement `SQLiteDatabase.mqh` class.
- [x] Integrate monthly partitioning logic.
- [x] Standardize volume normalization (Units/100 -> Lots).
- [x] Deploy automated maintenance routines (Vacuum/Integrity).

## 🎯 Quarter 1: The Kernel Rewrite (Foundational)
- [ ] Initialize Rust project workspace (`phoenix-core`).
- [ ] Implement **Lock-Free Event Bus** (`RingBuffer`) in Rust.
- [ ] Upgrade Security Layer to **AES-256-GCM**.
- [ ] Build **PyO3 Bridge** for Python-Rust event passing.

## 🚀 Immediate Next Steps (Database Testing)
- [ ] Test `SQLiteDatabase` with 1-year historical OHLCV data.
- [ ] Validate SL/TP detection accuracy in multi-symbol simulation.
- [ ] Verify `PerformMonthlyMaintenance()` scheduler reliability.
- [ ] Test automated S3-synced backup and restoration procedure.

## 🛡️ Quarter 4: Resilience & Visualization
- [ ] Build `ChaosMonkey` service for failure injection.
- [ ] Launch **FinCon Terminal V2** (Next.js/WebSockets).

---
**Success Metric:** Zero data loss at the broker edge during MT5 disconnects.
