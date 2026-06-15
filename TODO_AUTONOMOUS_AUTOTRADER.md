# 📝 GRANULAR TODO LIST: AAT PHASE 1 (IMPLEMENTATION)

## 🏗️ INFRASTRUCTURE (Week 1)
- [ ] **[INF-01]** Restructure repository to match `FINAL_ARCHITECTURE.md`.
- [ ] **[INF-02]** Initialize `config/main_config.json` with defaults.
- [ ] **[INF-03]** Implement `src/python/bridge/server.py` (Asyncio TCP).
- [ ] **[INF-04]** Implement `src/mql5/Include/AAT_BridgeClient.mqh` with Windows Sockets.
- [ ] **[INF-05]** Create PING/PONG heartbeat protocol between EA and Python.
- [ ] **[INF-06]** Build `src/python/hive/coordinator.py` for state management.

## 🧠 BRAIN ENGINE (Week 2)
- [ ] **[BRN-01]** Implement `src/python/brains/base_brain.py` (Abstract interface).
- [ ] **[BRN-02]** Implement `SequentialBrain.py` for Stage 1 signals.
- [ ] **[BRN-03]** Implement `ConsensusBrain.py` for Stage 2 voting logic.
- [ ] **[BRN-04]** Build Strategy Registry to dynamically load strategy plugins.
- [ ] **[BRN-05]** Implement first 3 strategies (EMA Cross, RSI, ADX).

## 🛡️ RISK & TRADE (Week 3)
- [ ] **[RSK-01]** Implement `src/python/risk/arbiter.py` (DD, Daily Loss, Sizing).
- [ ] **[RSK-02]** Implement ATR-based position sizing logic.
- [ ] **[TRD-01]** Implement `src/mql5/Include/AAT_TradeExecutor.mqh` (CTrade wrapper).
- [ ] **[TRD-02]** Implement SL/TP logic (fixed dollar + trailing).
- [ ] **[TRD-03]** Build `OnTradeTransaction` handler for position tracking.

## 📊 DASHBOARD & MONITORING (Week 4)
- [ ] **[DSH-01]** Implement `src/mql5/Include/AAT_UI_Grid.mqh` (CCanvas).
- [ ] **[DSH-02]** Create `AAT_GlobalDashboard.mq5` (Aggregator EA).
- [ ] **[DSH-03]** Implement real-time P&L and Risk telemetry push to Dash.
- [ ] **[MON-01]** Implement SQLite logging in `src/python/data/audit_logger.py`.

## 🧪 TESTING & HARDENING (Week 5)
- [ ] **[TST-01]** Write `tests/python/test_brains.py` for consensus accuracy.
- [ ] **[TST-02]** Write `tests/python/test_bridge_latency.py`.
- [ ] **[TST-03]** Perform L99 Verification Test #1: Python Crash Handling.
- [ ] **[TST-04]** Perform L99 Verification Test #2: Multi-Symbol Throughput.

## 🚀 DEMO & HANDOVER (Week 6)
- [ ] **[DEM-01]** Deploy to Demo account (EURUSD, XAUUSD).
- [ ] **[DEM-02]** Finalize `README.md` with accurate installation commands.
- [ ] **[DEM-03]** Prepare `DEEP_AUDIT_REPORT_FINAL.md`.
