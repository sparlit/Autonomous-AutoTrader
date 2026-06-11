# 🪐 Project Phoenix: Sovereign Execution Engine (V1.27)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.27 (Verified Edge Hardening)
**Focus:** High-Precision Resilience & Verified MQL5 Data Integrity.

✅ **Production Stable Core:** (MQL5/Python/Rust Hybrid)
✅ **Local Persistence:** (SQLite Partitioned Integration VERIFIED)
✅ **Governance Layer:** (PostgreSQL ACID + mTLS Hardened)
✅ **Refinement Protocol:** (41-Step Phoenix Protocol Integrated)
🔄 **Multi-Asset Autonomy:** (FX Focus Phase 1)

⚠️ **CRITICAL NOTE:** V1.27 codifies the **Verified SQLite Edge Implementation**. The terminal-side persistence layer has passed final implementation audit, ensuring that all trade volumes, symbol mappings, and maintenance routines meet institutional standards for "Zero-Loss" edge operations.

✅ **Core Integrity:** Modular Monolith / Hybrid Kernel.
✅ **Governance:** PostgreSQL (TimescaleDB) + SQLite (Local Edge Verified).
✅ **Standard:** L99-Standard V3 / MQL5-Verified Hardening.
🟡 **Hardening:** Implementation of 15-Layer Institutional Stack (Active).

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🗃️ MQL5 Local Persistence (Verified Integration)
The terminal-side persistence layer is now fully operational with the following specifications:
- **Monthly Table Partitioning:** Automated generation of `trades_YYYYMM`, `market_data_YYYYMM`, and `system_logs_YYYYMM`.
- **Automated Maintenance:** Mandatory `Vacuum()`, `IntegrityCheck()`, and `Backup()` routines performed via `PerformMonthlyMaintenance()`.
- **Configurable Retention:** Hard-coded 24-month retention period for local edge data.
- **Maintenance Cycle:** Reclaims unused space, verifies file integrity, and creates automated backups of the current month's data.

---

## 🔬 5. Quantitative Strategy & Model Governance
*Details the strategy development lifecycle, from research and backtesting to chaos stress testing and live incubation.*

### 📊 MQL5 Edge Verification Standards (V1.27)
Every MQL5 deployment must pass the following verification checklist:
1. **Volume Accuracy:** Confirmed volume conversion from broker units to lots (units/100.0).
2. **Table Consistency:** Uniform `{base}_YYYYMM` naming across all modules.
3. **Multi-Symbol Integrity:** Verified `HistoryDealString` usage for deal-to-symbol mapping.
4. **Position Tracking:** Accurate SL/TP detection through stateful position comparison.
5. **Stability:** Graceful degradation logic ensuring trading continues if DB is locked/unavailable.

---

## 🛡️ 6. Risk Management & Protective Layering
*The most critical section. It describes the multi-layered risk stack, including pre-trade checks, real-time exposure monitoring, and the automated kill switches.*

### 🛡️ MQL5 Local Risk Hardening
- **Local Error Handling:** Early returns in storage functions to prevent thread-locking.
- **Diagnostic Logging:** System logs stored locally for post-mortem analysis of risk events.
- **Persistence Fail-Safe:** Database unavailability triggers a "Safe-Mode" logging fallback but does not block order execution unless risk limits are indeterminate.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ MQL5 Execution Protocol (V1.27 Hardened)
The following execution standards are now hard-coded into the MQL5 adapter:
- **Volume Conversion Protocol:** Mandatory division of `DEAL_VOLUME` by 100.0 (e.g., `(double)volume/100.0`) at the moment of persistence.
- **Symbol Extraction Protocol:** Use of `HistoryDealString(trans.deal, DEAL_SYMBOL)` to eliminate symbol ambiguity in multi-broker environments.
- **Stateful Position Manager:** Position select by ticket logic to ensure accurate P&L and SL/TP attribution.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

### ⚖️ Hardened Local Audit Trail
- **Trade History Detail:** Stores ticket, action, close price, volume (in lots), profit, symbol, and high-precision timestamps.
- **Task Tracking:** Integrated `SetupTasks.mq5` module for database initialization and task completion auditing.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (Iterative Hardening)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Core Institutional Hardening
- [x] **Verified SQLite Database Implementation for MQL5.**
- [x] **Verified Volume Conversion Protocol (Units to Lots).**
- [x] **Verified Multi-Symbol Position Tracking.**
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
