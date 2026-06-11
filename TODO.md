# 🗂️ Project Phoenix V7.1.0 — Master Revamp TODO (V1.28)

## Epic 1 — PHASE 1: MVP & Hardened Core (Months 0-6)
### 🔴 Infrastructure & Foundation
- [x] **I-1.1** SQLite Database Implementation (Partitioned).
- [x] **I-1.2** Volume Conversion Fix (Units to Lots).
- [x] **I-1.3** Multi-Symbol Extraction Logic.
- [ ] **I-1.4** PostgreSQL 15+ (Primary + Sync Standby).

### 🔴 Core Engine & Multi-Symbol
- [x] **C-1.1** Define `SymbolContext` structure and global arrays.
- [ ] **C-1.2** Refactor `OnInit()` to parse `SymbolList`.
- [ ] **C-1.3** Implement Magic Offset Protocol (Base 700070).
- [ ] **C-1.4** Refactor `OnTick()` for parallel symbol iteration.
- [ ] **C-1.5** Update `OnTradeTransaction()` for magic matching.

### 🟠 Model & Strategy
- [ ] **S-1.2** MVP Strategy (Mean Reversion, half-Kelly).

## 🚀 Immediate Next Steps (Multi-Symbol Implementation)
1. Add `SymbolContext` struct to `Symbols.mqh`.
2. Rewrite `OnInit()` parser for comma-separated `SymbolList`.
3. Update all indicator initialization to use per-symbol handles.

---
**Status:** 🏗️ MULTI-SYMBOL INTEGRATION | **Target Hours:** 12,000 | **Success Metric:** zero capital loss under 1000 chaos tests.
