# Project Phoenix Revamp TODO - V1.11 (Technical Protocol)

## Epic 1 — MQL5 Autonomous Implementation
- [ ] **Task 1:** Extend SymbolContext structure in `Symbols.mqh` with `dailyPnL`, `lotSize`, `stopLoss`, `atrValue`, and signal flags.
- [ ] **Task 2:** Add global risk variables in `AutoTraderPro.mq5` (`dailyStartEquity`, `tradingEnabled`).
- [ ] **Task 3:** Initialize daily loss tracking in `OnInit()`.
- [ ] **Task 4:** Create `RiskManagement.mqh` with `ResetDailyLossIfNeeded()` and `CheckDailyLossLimit()` (2% cap).
- [ ] **Task 5:** Integrate daily loss checks into `OnTick()` loop.
- [ ] **Task 6:** Implement `CalculateLotSize()` using fixed 1% risk of equity and stop loss distance.
- [ ] **Task 7:** Implement `CalculateATRAndLevels()` for SL (1.5x ATR) and TP (3.0x ATR).
- [ ] **Task 8:** Refactor `AnalyzeAndTrade()` for full autonomous signal execution (MA Cross 9/21).
- [ ] **Task 9:** Update `OpenTrade()` to use `ctx->magicBase` for symbol-independent tracking.
- [ ] **Task 10:** Implement ATR-based Trailing Stops (1.0x ATR) and 24-hour time exits in `ManagePositions()`.
- [ ] **Task 11:** Enhance Dashboard with real-time portfolio risk metrics and trading status.
- [ ] **Task 12:** Full Strategy Tester validation across major pairs (EURUSD, GBPUSD, USDJPY).

## Epic 2 — Foundation & Core Integrity
- [x] Audit EventBus circular dependencies; refactor to explicit contracts.
- [ ] Implement Event Sourcing (CQRS) with Snapshotting.
- [ ] Set up Docker/K8s dev/prod parity.

## Epic 3 — Risk & Resilience Hardening
- [ ] Build Exposure Graph for currency/factor correlations.
- [ ] Implement Pre-trade Monte Carlo Sandbox.

## Epic 4 — Execution & Broker Health
- [ ] Implement Broker Health Scorer.
- [ ] Build dual-broker failover prototype.

## Epic 5 — Operations & Documentation
- [ ] Define on-call runbooks.
- [ ] Establish post-trade review rituals.

## Success Metrics
- Zero critical bugs in shadow trading for 1 month.
- 5-10% Monthly Return with < 10% Drawdown.
