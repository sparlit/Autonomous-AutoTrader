# 🪐 Project Phoenix: Sovereign Execution Engine (V1.33)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.33 (Volume Normalization Validation)
**Focus:** High-Precision Resilience & Verified Execution Analytics.

✅ **Production Stable Core:** (MQL5/Python/Rust Hybrid)
✅ **Local Persistence:** (SQLite Partitioned Integration COMPLETE)
✅ **Volume Normalization:** (100:1 Unit-to-Lot Conversion VERIFIED)
✅ **Governance Layer V2:** (Pre-Computed Context)
🔄 **Multi-Asset Autonomy:** (FX Focus Phase 1)

⚠️ **CRITICAL NOTE:** V1.33 codifies the **100:1 Volume Conversion Protocol**. In compliance with MQL5 `DEAL_VOLUME` standards, all terminal-side deal data is normalized to standard lots (Units/100.0) at the point of persistence to eliminate statistical skew in trade history and equity accounting.

✅ **Core Integrity:** Modular Monolith / Hybrid Kernel.
✅ **Governance:** PostgreSQL (Institutional) + SQLite (Edge Local).
✅ **Standard:** L99-Standard V3 / Precise-Volume Certified.
🟡 **Hardening:** Implementation of 15-Layer Institutional Stack (Active).

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🗃️ 4.2 MQL5 Edge Persistence (SQLite Core)
The terminal-side persistence layer ensures local data sovereignty and recovery:
- **Standard Local Path:** `E:\myproject\mql\autotrader.db`
- **Monthly Table Partitioning:** Automated generation of `trades_YYYYMM`, `market_data_YYYYMM`, and `system_logs_YYYYMM`.
- **Performance Standard:** **WAL (Write-Ahead Logging)** mode enabled.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Execution Standards (V1.33)
- **100:1 Volume Normalization:** All deal volumes extracted via `DEAL_VOLUME` (units) must be divided by 100.0 to convert to standard lots before storage or risk calculation (e.g., `(double)volume/100.0`).
- **Functional Alignment:** Verified that all `StoreTradeData` calls (Open, Partial Close, Time Exit, Final Close) use lot-normalized volume.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (V7.1)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: The Hybrid Kernel (Current)
- [x] Implement Persistent SQLite Database for MQL5 (Partitioned).
- [x] **Verify 100:1 Volume Normalization Fix.**
- [ ] Port Event Bus to Rust (Lock-free Ring Buffer).

---

## 📜 17. Appendices & Data Dictionary
*Capital preservation is the primary outcome of discipline.*
