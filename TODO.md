# 🗂️ Project Phoenix V7.1.0 — Master Revamp TODO (V1.27)

## Epic 1 — PHASE 1: MVP & Hardened Core (Months 0-6)
### 🔴 Infrastructure & Foundation
- [x] **I-1.1** SQLite Database Implementation (Partitioned, Maintenance).
- [x] **I-1.2** Volume Conversion Fix (Units to Lots).
- [x] **I-1.3** Multi-Symbol Extraction Logic (HistoryDealString).
- [ ] **I-1.4** Dev Env Setup (Docker, Vault, mTLS).
- [ ] **I-1.5** PostgreSQL 15+ (Primary + Sync Standby, RAFT).

### 🔴 Core Engine & Risk
- [x] **C-1.1** MQL5 Local Persistence Module (`SQLiteDatabase.mqh`).
- [x] **C-1.2** Consistent Table Naming Logic (`trades_YYYYMM`).
- [ ] **C-1.3** FastAPI/Rust Hybrid Foundation.

### 🟠 Model & Strategy
- [ ] **S-1.2** MVP Strategy (Mean Reversion, half-Kelly).
- [ ] **A-1.1** Cryptographic Audit Trail (PostgreSQL side).

## 🚀 Immediate Next Steps (MQL5 Testing)
1. **Compile** all modified .mq5 files in MetaEditor.
2. **Run** `SetupTasks.mq5` to initialize database.
3. **Monitor** trade storage after position closures (verify volume in lots).
4. **Test** maintenance routines via `PerformMonthlyMaintenance()`.

---
**Status:** 🛡️ EDGE PERSISTENCE VERIFIED | **Target Hours:** 12,000 | **Success Metric:** zero capital loss under 1000 chaos tests.
