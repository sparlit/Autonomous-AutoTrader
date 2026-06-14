# AAT Phase 1 Implementation Plan — The Bridge Builder

**Date**: 2026-06-14
**Status**: In Progress
**Approach**: Layered bottom-up (Bridge → Dashboard → Strategy → Risk → Integration → Demo)

---

## Week 1: Project Structure + Socket Bridge Foundation

### 1.1 Finalize Project Structure
- [ ] Verify `_archive/` has all 30 legacy .mq5 files
- [ ] Verify `src/mql5/experts/`, `src/mql5/include/`, `src/mql5/scripts/` populated
- [ ] Verify `src/python/` has 5 renamed Python modules (no version suffixes)
- [ ] Verify `scripts/`, `config/`, `tests/` exist
- [ ] Create `config/aat_config.json` with default runtime settings
- [ ] Create `config/vault.json.enc` placeholder (encrypted API keys)
- [ ] Update `requirements.txt` with needed packages (cryptography, websockets, etc.)
- [ ] Delete root `SKILL.md` (empty placeholder)

### 1.2 MQL5 Socket Client (`src/mql5/include/AAT_SocketClient.mqh`)
- [ ] Rename `AAT-SocketClient-V1.0.0.mqh` → `AAT_SocketClient.mqh`
- [ ] Define `CAATSocketClient` class: `Connect()`, `Disconnect()`, `SendJSON()`, `ReceiveJSON()`
- [ ] Implement TCP socket: `SocketCreate()`, `SocketConnect()`, `SocketSend()`, `SocketReceive()`
- [ ] Connection state enum: `DISCONNECTED`, `CONNECTING`, `CONNECTED`, `ERROR`
- [ ] Basic PING/PONG heartbeat (10s interval)
- [ ] Connection timeout (5s per spec)
- [ ] Reconnection with exponential backoff stub

### 1.3 Python Protocol + Server (`src/python/AAT_Protocol.py`)
- [ ] Create `AAT_Protocol.py` with message type constants + JSON envelope builder
- [ ] Define all 7 message types: PING, PONG, OHLC_PUSH, ANALYSIS_REQ, CONSENSUS_RSP, RISK_CHECK, RISK_RSP
- [ ] Create `AAT_Config.py` with centralized config (host, port, heartbeat, thresholds)
- [ ] Async TCP server using Python `asyncio` + `socket`
- [ ] Basic PING/PONG handler
- [ ] Test bidirectional PING/PONGO

### 1.4 JSON Parser (`src/mql5/include/AAT_JsonParser.mqh`)
- [ ] Rename `AAT-JsonParser-V1.0.0.mqh` → `AAT_JsonParser.mqh`
- [ ] Refine parser for all 7 message types
- [ ] Add validation: required fields, type coercion, NaN detection

**Week 1 Gate**: PING/PONG works bidirectionally over TCP

---

## Week 2: Secure Bridge + All Message Types + Fallback

### 2.1 AES-256-CBC Encryption
- [ ] Add AES-256-CBC encryption to `AAT_SocketClient.mqh`
- [ ] Add AES-256-CBC decryption to Python server (`cryptography` lib)
- [ ] Shared secret derivation from `vault.json.enc`
- [ ] IV exchange protocol (prepend IV to ciphertext)
- [ ] Test: encrypt MQL5 → decrypt Python → byte-identical

### 2.2 Token Authentication
- [ ] Token-based auth on connection handshake
- [ ] Derive auth token from vault secret
- [ ] Reject unauthenticated connections server-side

### 2.3 All Message Types
- [ ] OHLC_PUSH: EA detects new bar → sends candle array
- [ ] ANALYSIS_REQ: EA requests strategy analysis (symbol, strategy)
- [ ] CONSENSUS_RSP: Python returns consensus + direction + strategies fired
- [ ] RISK_CHECK: EA sends trade params (symbol, direction, lots, entry_price)
- [ ] RISK_RSP: Python returns approval + reason + adjusted_lots
- [ ] Test all 7 types integration

### 2.4 Fallback Chain
- [ ] File-based IPC: MQL5 writes `/tmp/aat_msg_out.json`, reads `/tmp/aat_msg_in.json`
- [ ] Python reads/writes same file paths
- [ ] Socket failure → auto-switch to file IPC within 5s
- [ ] Background retry: every 30s try socket reconnect
- [ ] Socket recovery → flush file queue → resume socket mode
- [ ] Test: kill Python → EA switches to file → restart → EA reconnects

**Week 2 Gate**: All 7 types + encryption + fallback verified

---

## Week 3: Dashboard (CCanvas)

### 3.1 Dashboard Core (`src/mql5/include/AAT_Dashboard.mqh`)
- [ ] Rename `AAT-Dashboard-V1.0.0.mqh` → `AAT_Dashboard.mqh`
- [ ] `CAATDashboard` class with CCanvas rendering
- [ ] 3-tab system: HEALTH, LIVE_ANALYTICS, SETTINGS
- [ ] Tab switching via mouse click

### 3.2 Tab 1: HEALTH & SAFETY
- [ ] Symbol grid: M1,M5,M15,M30,H1,H4,D1,W1 + consensus column
- [ ] Direction arrows: ▲ ▼ ─ with color coding
- [ ] Health bar: OK/ERROR, heartbeat, engine latency, VaR, spread, P&L, regime
- [ ] Active signal alert: ⚠ BUY EURUSD │ CONF: 85% │ STRATS: 4/5
- [ ] Status bar: Connected, Trades, Win%, Uptime

### 3.3 Tab 2: LIVE ANALYTICS
- [ ] Per-signal expandable details
- [ ] Strategy breakdown table
- [ ] Confidence histogram

### 3.4 Tab 3: SETTINGS
- [ ] Risk % input
- [ ] Strategy toggles
- [ ] Trailing stop parameters

### 3.5 Performance Safeguards
- [ ] 500ms render throttle
- [ ] Eco-mode: 1 FPS hidden, 30 FPS visible
- [ ] `OnChartEvent()` visibility change detection

### 3.6 Theme
- [ ] Cyber-Pro Dark (neon green/red, semi-transparent charcoal, animated pulse)
- [ ] Bitmap fonts with MT5 fallback

**Week 3 Gate**: Dashboard renders all 3 tabs with live engine data

---

## Week 4: Strategy Engine + Risk Manager (Python)

### 4.1 StrategyMaster (`src/python/AAT_StrategyMaster.py`)
- [ ] Refactor with clean class structure
- [ ] Multi-TF Trend Consensus:
  - EMA Cross (M5): 12/26 EMA → BUY=+1, SELL=-1, NEUTRAL=0
  - RSI Zone (H1): RSI(14) <30=+1, >70=-1, else=0
  - ADX (H1): >25=+0.5, <20=-0.5, else=0
  - VWAP (M15): above=+0.5, below=-0.5
  - Sentiment (D1): BULLISH=+1, BEARISH=-1, NEUTRAL=0
- [ ] Weighted consensus: EMA 30%, RSI 20%, ADX 20%, VWAP 15%, Sentiment 15%
- [ ] Threshold: |score| ≥ 0.7
- [ ] Return CONSENSUS_RSP with direction, confidence, strategies_fired
- [ ] 100% unit test coverage

### 4.2 RiskManager (`src/python/AAT_RiskManager.py`)
- [ ] Refactor with clean class structure
- [ ] Position sizing: `Lot = (Equity × Risk%) / (ATR × PipsValue)`
- [ ] Max drawdown halt: DD > 5% → halt all
- [ ] Daily loss limit: > 2% → stop for day
- [ ] Consecutive loss pause: 3 losses → 30min cooldown
- [ ] Spread filter: > 2× average → skip
- [ ] Slippage guard: > 10% of profit → abort
- [ ] Cool-down: close all + notify + 4h pause on DD breach
- [ ] Return RISK_RSP: {approved, reason, adjusted_lots}
- [ ] 100% unit test coverage

### 4.3 Config (`src/python/AAT_Config.py`)
- [ ] Centralized config class
- [ ] Load from `config/aat_config.json` with defaults
- [ ] All tunable params: risk%, heartbeat interval, socket host/port, weights, thresholds

**Week 4 Gate**: StrategyMaster + RiskManager pass 100% unit tests

---

## Week 5: MQL5 Trading Engine Integration

### 5.1 TradingEngine (`src/mql5/include/AAT_TradingEngine.mqh`)
- [ ] Create `AAT_TradingEngine.mqh` with `CAATTradingEngine`
- [ ] `OnTick()` flow: detect new bar → push OHLC → request analysis → receive consensus → risk check → execute
- [ ] CTrade integration: `Buy()`, `Sell()`, `PositionModify()`
- [ ] Order result handling: DONE→success, else→retry once→halt

### 5.2 StrategyRegistry (`src/mql5/include/AAT_StrategyRegistry.mqh`)
- [ ] Create `AAT_StrategyRegistry.mqh` with `CAATStrategyRegistry`
- [ ] Register strategies by name, enable/disable toggle
- [ ] Dashboard settings reads/writes registry state
- [ ] Active strategy list in ANALYSIS_REQ payload

### 5.3 Main EA (`src/mql5/experts/AAT_Expert.mq5`)
- [ ] `OnInit()`: Init socket, dashboard, trading engine, registry
- [ ] `OnTick()`: Delegate to trading engine
- [ ] `OnDeinit()`: Graceful shutdown
- [ ] `OnChartEvent()`: Dashboard interaction
- [ ] `OnTimer()`: Heartbeat check + stale data detection

### 5.4 Signal Flow Verification
- [ ] Test: OHLC push → analysis → consensus → risk → execution (demo)
- [ ] Test: Rejected consensus (|score| < 0.7) → no trade
- [ ] Test: Risk rejection → no trade, reason logged

**Week 5 Gate**: End-to-end signal flow works

---

## Week 6: Error Handling + Resilience + Testing

### 6.1 Three-Layer Error Strategy (MQL5)
- [ ] PREVENT: Input validation, capability checks, pre-flight heartbeat
- [ ] DETECT: Bidirectional heartbeat (10s), NaN/stale detection, state reconciliation
- [ ] RECOVER: Exponential backoff (1s→2s→4s→8s→max30s), break-even fail-safe, emergency close, file IPC hot-swap

### 6.2 Zero-Stub Retry (Python)
- [ ] `retry_with_backoff()` in `AAT_MainEngine.py`
- [ ] Applied to every external call
- [ ] Max 5 attempts, max 30s delay

### 6.3 Risk Hardening
- [ ] Zero lots on invalid ATR
- [ ] Equity spike: >10% in 60s → emergency halt + force-close
- [ ] Watchdog: heartbeat >15s → positions to break-even
- [ ] Network partition: all fail → SL to break-even + halt

### 6.4 Python Unit Tests
- [ ] `tests/test_bridge.py`: 7 message types, encryption, fallback
- [ ] `tests/test_strategies.py`: signals, consensus, thresholds
- [ ] `tests/test_risk.py`: sizing, halts, edge cases

**Week 6 Gate**: All error scenarios handled + unit tests pass

---

## Week 7: Integration Testing + Demo Prep

### 7.1 L99 Verification Tests (Must All Pass)
- [ ] Bridge survives Python crash → EA halts <30s, no unprotected trades
- [ ] File fallback → EA receives consensus via file within 60s
- [ ] All 11 timeframes push correctly
- [ ] Consensus threshold blocks |score| < 0.7
- [ ] Position sizing → zero on invalid ATR
- [ ] 3 consecutive losses → 30min cooldown
- [ ] 5% drawdown halts trading
- [ ] Spread > 2× average aborts trade
- [ ] AES-256 roundtrip byte-identical
- [ ] Watchdog: heartbeat >15s → positions to break-even

### 7.2 Demo Configuration
- [ ] `config/aat_config.json`: EURUSD, single strategy, conservative risk
- [ ] Python startup script
- [ ] MT5 chart template with AAT_Expert
- [ ] Demo account configured

**Week 7 Gate**: All L99 tests pass

---

## Week 8: Demo Dry-Run + Validation

### 8.1 Demo Execution (1 week, EURUSD, 1 strategy)
- [ ] Start demo with monitoring
- [ ] Daily review: trade count, P&L, DD, exceptions, latency

### 8.2 Demo Gates (Must Pass for Phase 2)
- [ ] 50+ trades with positive expectancy
- [ ] Zero unhandled exceptions in 4 weeks
- [ ] Heartbeat <5s median latency
- [ ] All risk halts tested (DD>5%, daily>2%, 3-loss, spread, slippage)
- [ ] Dashboard reflects engine state

### 8.3 Sign-Off
- [ ] Document demo results
- [ ] Fix remaining bugs
- [ ] Phase 1 completion approval
- [ ] Begin Phase 2 planning

---

## New Files to Create

| File | Week | Purpose |
|------|------|---------|
| `src/python/AAT_Protocol.py` | 1 | Message protocol definitions |
| `src/python/AAT_Config.py` | 4 | Centralized configuration |
| `src/mql5/include/AAT_TradingEngine.mqh` | 5 | Trade execution |
| `src/mql5/include/AAT_StrategyRegistry.mqh` | 5 | Strategy management |
| `config/aat_config.json` | 1 | Runtime config |
| `config/vault.json.enc` | 2 | Encrypted keys |
| `tests/test_bridge.py` | 6 | Bridge tests |
| `tests/test_strategies.py` | 6 | Strategy tests |
| `tests/test_risk.py` | 6 | Risk tests |

## Files to Rename (Strip Version Suffixes)

| Current | Target | Week |
|---------|--------|------|
| `AAT-Dashboard-V1.0.0.mqh` | `AAT_Dashboard.mqh` | 3 |
| `AAT-JsonParser-V1.0.0.mqh` | `AAT_JsonParser.mqh` | 1 |
| `AAT-SocketClient-V1.0.0.mqh` | `AAT_SocketClient.mqh` | 1 |