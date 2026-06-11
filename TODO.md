# 🗂️ Project Phoenix V7.1.0 — Master Revamp TODO (V1.26)

## Epic 1 — PHASE 1: MVP & Hardened Core (Months 0-6)
### 🔴 Infrastructure & Foundation
- [x] **I-1.1** SQLite Database Implementation (Partitioned, Maintenance).
- [x] **I-1.2** Volume Conversion Fix (Units to Lots).
- [ ] **I-1.3** Dev Env Setup (Docker, Vault, mTLS).
- [ ] **I-1.4** PostgreSQL 15+ (Primary + Sync Standby, RAFT).

### 🔴 Core Engine & Risk
- [x] **C-1.1** MQL5 Local Persistence Module (`SQLiteDatabase.mqh`).
- [x] **C-1.2** Consistent Table Naming Logic (`trades_YYYYMM`).
- [ ] **C-1.3** FastAPI/Rust Hybrid Foundation.

### 🟠 Model & Strategy
- [ ] **S-1.2** MVP Strategy (Mean Reversion, half-Kelly).
- [ ] **A-1.1** Cryptographic Audit Trail (PostgreSQL side).

## Epic 2 — PHASE 2: Institutional Core
- [ ] **F-2.1** FIX 4.4/5.0 Gateway.
- [ ] **G-2.1** Drift Detection & Meta-governance.

---
**Status:** 🔄 LOCAL PERSISTENCE COMPLETE | **Target Hours:** 12,000 | **Success Metric:** zero capital loss under 1000 chaos tests.
