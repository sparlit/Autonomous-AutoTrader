# 📝 DEEP-DIVE GRANULAR TODO LIST: AAT PHASE 1

## 🏗️ LAYER 1: INFRASTRUCTURE & CONNECTIVITY (WEEK 1)

### [INF-01] Repository Restructuring
- [ ] Create directory structure: `config/`, `src/python/hive/`, `src/python/brains/`, `src/python/bridge/`, `src/mql5/Agents/`, `src/mql5/Dash/`, `src/mql5/Include/`.
- [ ] Move existing design docs to `docs/`.
- [ ] Migrate `requirements.txt` to root and add: `asyncio`, `pyyaml`, `pydantic`, `numpy`, `pandas`.

### [INF-02] Configuration System
- [ ] Create `config/main_config.json` with schema for: `bridge_port`, `heartbeat_interval`, `risk_params`, `brain_parallelism`.
- [ ] Create `config/symbols.json` mapping MT5 symbols to Yahoo tickers.
- [ ] Implement `src/python/hive/config_loader.py` with Pydantic validation.

### [INF-03] Async TCP Bridge (Python)
- [ ] Implement `src/python/bridge/server.py` using `asyncio.start_server`.
- [ ] Create `MessageCodec` for JSON/Protobuf serialization.
- [ ] Implement `ClientHandler` class to manage multiple MT5 Agent connections.

### [INF-04] Socket Bridge Client (MQL5)
- [ ] Implement `src/mql5/Include/AAT_SocketClient.mqh` using WinAPI `ws2_32.dll`.
- [ ] Functions: `Connect()`, `Disconnect()`, `Send()`, `Receive()`, `IsConnected()`.
- [ ] Logic for non-blocking I/O to prevent chart freezing.

### [INF-05] Heartbeat & Watchdog
- [ ] Implement 10s PING/PONG in `AAT_SocketClient.mqh`.
- [ ] Implement `src/python/bridge/watchdog.py` to detect stale agents.
- [ ] Logic in MQL5 to switch to "Safe Mode" (Move SL to BE) if heartbeat fails.

---

## 🧠 LAYER 2: THE MULTI-BRAIN ENGINE (WEEK 2)

### [BRN-01] Brain Interface & Registry
- [ ] Create `src/python/brains/base.py` (Abstract Base Class).
- [ ] Implement `BrainRegistry` for dynamic loading of .py strategy files.
- [ ] Define `SignalPayload` schema (symbol, tf, direction, confidence).

### [BRN-02] Sequential Brain (Stage 1: Fast-Path)
- [ ] Implement `src/python/brains/sequential_brain.py`.
- [ ] Logic: Iterative execution of `S01-S05`. Return first non-neutral signal.
- [ ] Integration with Veto Filters (Spread, News).

### [BRN-03] Consensus Brain (Stage 2: Voting-Path)
- [ ] Implement `src/python/brains/consensus_brain.py`.
- [ ] Logic: Parallel execution of `S06-S20` using `asyncio.gather`.
- [ ] Weight-weighted summation: `Score = Σ (Signal * Weight)`.
- [ ] Threshold check: `|Score| >= 0.7`.

### [BRN-04] Core Strategies (Initial Set)
- [ ] `S01_VetoFilter`: Spread check + Master kill switch.
- [ ] `S06_EMACross`: M5 Trend signal.
- [ ] `S07_RSI_Momentum`: H1 Overbought/Oversold.

---

## 🛡️ LAYER 3: RISK & TRADE EXECUTION (WEEK 3)

### [RSK-01] The Risk Arbiter
- [ ] Implement `src/python/risk/arbiter.py`.
- [ ] Global Daily Loss check (2% threshold).
- [ ] Max Drawdown check (5% threshold).
- [ ] Multi-symbol correlation filter (don't overexpose to USD).

### [RSK-02] Dynamic Position Sizing
- [ ] Implement ATR-based sizing: `Lots = (Equity * Risk%) / (ATR * PipValue)`.
- [ ] Logic to round lots to broker steps (e.g., 0.01).
- [ ] Minimum lot size validation.

### [TRD-01] Trade Executor (MQL5)
- [ ] Implement `src/mql5/Include/AAT_Trade.mqh`.
- [ ] Wrapper for `CTrade`: `ExecuteBUY()`, `ExecuteSELL()`, `ModifyPosition()`.
- [ ] Handle `TRADE_RETCODE_DONE` and common error codes.

---

## 📊 LAYER 4: DASHBOARD & TELEMETRY (WEEK 4)

### [DSH-01] Dashboard Engine (MQL5)
- [ ] Implement `src/mql5/Include/AAT_Dashboard.mqh` using `CCanvas`.
- [ ] 3-Tab System: [HEALTH] [BRAINS] [RISK].
- [ ] High-FPS rendering (throttle to 500ms).

### [DSH-02] Global Dashboard EA
- [ ] Create `src/mql5/Dash/AAT_GlobalDashboard.mq5`.
- [ ] Logic to aggregate state from the Python Coordinator.
- [ ] Visual signal alerts (Neon Green/Red).

### [MON-01] Audit Logger (SQLite)
- [ ] Implement `src/python/data/audit_logger.py`.
- [ ] Table schema: `timestamp, symbol, brain_type, signal, confidence, decision, risk_reason`.
- [ ] Automatic daily log rotation.

---

## 🧪 LAYER 5: HARDENING & L99 VALIDATION (WEEK 5)

### [TST-01] Integration Testing
- [ ] Script to spawn Mock Agent and verify Python Coordinator response.
- [ ] Test: Network Disconnect recovery.
- [ ] Test: 3 Consecutive Losses → Cooldown activation.

### [TST-02] L99 Verification
- [ ] **L99-01**: Kill Python process while Agent has open trade → Agent moves SL to BE.
- [ ] **L99-02**: Simulate 10% slippage → Risk Arbiter rejects trade.
- [ ] **L99-03**: Multi-symbol stress test (6 symbols, high frequency).

---

## 🚀 LAYER 6: ROLLOUT & HANDOVER (WEEK 6)

### [DEM-01] Demo Deployment
- [ ] Set up VPS with Python 3.10 and MT5 Terminal.
- [ ] Deploy EURUSD Agent on H1 chart.
- [ ] 24/5 Live monitoring and log audit.

### [DEM-02] Final Handover
- [ ] Finalize `README.md` with "Zero-Stub" verification instructions.
- [ ] Prepare Phase 2 Roadmap.
