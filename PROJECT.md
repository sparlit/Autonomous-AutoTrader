# 🪐 Project Phoenix: Sovereign Execution Engine (V1.26)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.26 (Local Persistence Validation)
**Focus:** High-Precision Resilience & MQL5 Data Integrity.

✅ **Production Stable Core:** (MQL5/Python/Rust Hybrid)
✅ **Local Persistence:** (SQLite Partitioned Integration COMPLETE)
✅ **Governance Layer:** (PostgreSQL ACID + mTLS Hardened)
✅ **Refinement Protocol:** (41-Step Phoenix Protocol Integrated)
🔄 **Multi-Asset Autonomy:** (FX Focus Phase 1)

⚠️ **CRITICAL NOTE:** V1.26 integrates the **SQLite Local Database Completion**. While PostgreSQL remains the institutional audit standard, SQLite is codified as the mandatory local partitioned store for edge-side terminal persistence (Trades, Market Data, System Logs).

✅ **Core Integrity:** Modular Monolith / Hybrid Kernel.
✅ **Governance:** PostgreSQL (TimescaleDB) + SQLite (Local Edge Partitioned).
✅ **Standard:** L99-Standard V3 / MQL5-Edge Certified.
🟡 **Hardening:** Implementation of 15-Layer Institutional Stack (Active).

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🗃️ MQL5 Local Persistence (SQLite Integration)
The terminal-side persistence layer is now fully operational with the following specifications:
- **Monthly Table Partitioning:** Automated generation of `trades_YYYYMM`, `market_data_YYYYMM`, and `system_logs_YYYYMM`.
- **Automated Maintenance:** Mandatory `Vacuum()`, `IntegrityCheck()`, and `Backup()` routines performed monthly.
- **Configurable Retention:** Hard-coded 24-month retention period for local edge data.
- **Data Integrity:** Graceful degradation logic ensuring trading continues even if local persistence is temporarily unavailable.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Execution Protocol (V1.26)
The following execution standards are now hard-coded into the MQL5 adapter:
- **Volume Conversion Fix:** All deal volumes from `DEAL_VOLUME` must be divided by 100.0 (e.g., `(double)volume/100.0`) to convert from broker units to standard lots.
- **Symbol Extraction:** Mandatory use of `HistoryDealString(deal, DEAL_SYMBOL)` for accurate multi-symbol history reconstruction.
- **Position Tracking:** Accurate SL/TP detection through comparative position analysis.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

### ⚖️ Local Audit Specifications
- **Trade History:** Full decision provenance including ticket, action, price, volume, and profit stored in partitioned monthly tables.
- **Table Consistency:** Uniform naming format `{base}_{YYYYMM}` enforced across all MQL5 modules (`trades_202606`, etc.).

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (Iterative Hardening)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Core Institutional Hardening
- [x] **Complete SQLite Database Implementation for MQL5.**
- [x] **Implement Volume Conversion Fix (Units to Lots).**
- [ ] Transition to **AES-256-GCM** and **mTLS**.

---

## 📜 12. Phoenix Standardized Refinement Protocol (41 Steps)
*Mandatory operational lifecycle for achieving project-wide technical excellence.*

---

## 📜 13. Sovereign Operational Rituals (V1.21)
*Mandatory daily rituals to ensure the alignment of the human-machine sovereign ensemble.*

---

## 🌌 14. Advanced Intelligence Synthesis (V1.23)
*Conceptual abstractions from the "1000 Years Ahead" perspective.*

---

## 📜 15. Appendices & Data Dictionary
*Capital preservation is the primary objective; profit is a secondary outcome of discipline.*
