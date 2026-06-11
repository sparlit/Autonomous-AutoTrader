# 🪐 Project Phoenix: Sovereign Execution Engine (V1.28)

## 🏛️ 1. Project Identity & Sovereign Governance
*This section defines the core identity of Project Phoenix, its current operational status, and the governance framework that ensures its integrity. It serves as the primary source of truth for the system's versioning and its adherence to institutional standards.*

### 📍 Status: The Global Revamp (Post-Autopsy)
**Operational Mode:** Phoenix V1.28 (Multi-Symbol Alignment)
**Focus:** High-Precision Resilience & Multi-Asset Sovereignty.

✅ **Production Stable Core:** (MQL5/Python/Rust Hybrid)
✅ **Local Persistence:** (SQLite Partitioned Integration VERIFIED)
🔄 **Multi-Symbol Logic:** (SymbolContext Architecture Integration)
🔄 **Multi-Asset Autonomy:** (FX Focus Phase 1)

⚠️ **CRITICAL NOTE:** V1.28 integrates the **Multi-Symbol Architecture Guide**. We transition from single-pair limitations to a parallel execution framework where each symbol operates within its own `SymbolContext`, ensuring zero interference between assets.

✅ **Core Integrity:** Modular Monolith / Parallel Context Architecture.
✅ **Governance:** PostgreSQL (Institutional) + SQLite (Edge Context-Aware).
✅ **Standard:** L99-Standard V3 / Multi-Symbol Protocol V1.
🟡 **Hardening:** Implementation of 15-Layer Institutional Stack (Active).

---

## 🏗️ 4. System Architecture & Institutional Technology Stack
*A comprehensive blueprint of the system's technical design. This includes the 'Sovereign Trinity' (Ingress, Logic, Persistence), the high-performance event bus, and the database schema strategy.*

### 🏗️ MQL5 Multi-Symbol Architecture (V1.28)
The engine is structured for parallel multi-asset trading from a single chart instance:
- **SymbolContext Container:** Each symbol maintains an independent state including:
  - `AutoParams P`: Per-symbol optimized parameters.
  - `PerformanceStats`: Real-time P&L and drawdown for the specific asset.
  - `Regime`: Independent market regime detection.
  - `hIndicators`: Independent handles for all technical analysis (Fast, Slow, Trend, ATR, etc.).
- **Global Context Array:** `SymbolContext Symbols[10]` manages the active portfolio.
- **Magic Offset Protocol:** To ensure unique identification, magic numbers are calculated as `Base(700070) + (SymbolID * 100)`.

---

## 🌐 7. Market Connectivity & Execution Intelligence
*Outlines the protocols and strategies used to interface with liquidity providers.*

### 🏛️ Multi-Symbol Execution Protocol
- **Symbol-Independent Lifecycle:**
  - `OnInit()`: Parses `SymbolList` inputs and initializes individual contexts.
  - `OnTick()`: Iterates through the `Symbols[]` array, triggering independent analysis and execution logic.
  - `OnTradeTransaction()`: Uses the magic offset to match transactions back to their originating `SymbolContext`.
  - `OnDeinit()`: Systematic release of all context-bound indicator handles.
- **Unified Risk Integration:** Individual symbol contexts are audited by the global portfolio risk engine before order emission.

---

## 📜 9. Regulatory Compliance & Audit Provenance
*Ensures the system meets all legal and regulatory requirements (MiFID III, Basel III, GDPR).*

### ⚖️ Multi-Symbol Audit Standards
- **Context-Aware Journaling:** CSV and SQLite journals must track all symbols separately using the `magicOffset` as the primary key.
- **Independent Optimization:** Every symbol must maintain its own `LastOptimizeTime` and `LastReviewTime` record for compliance purposes.

---

## 🗺️ 11. Strategic Roadmap: Sovereign Ascent (Iterative Hardening)
*The chronological plan for the project's evolution.*

### 📍 Phase 1: Core Institutional Hardening
- [x] Verified SQLite Database Implementation for MQL5.
- [x] **Implement SymbolContext Multi-Symbol Architecture.**
- [x] **Deploy Magic Number Offset Protocol (+100 per asset).**
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
