# Autonomous AutoTrader (AAT) - Phase 1 Design: The Bridge Builder

**Date**: 2026-06-14  
**Approach**: Layered bottom-up  
**Phase**: 1 of 4 (Foundation: EA + Bridge + Dashboard)  
**Status**: Approved  

---

## Table of Contents
1. [Project Structure & Cleanup](#1-project-structure--cleanup)
2. [Socket Bridge Protocol](#2-socket-bridge-protocol)
3. [Dashboard Architecture](#3-dashboard-architecture)
4. [Strategy Engine (Phase 1 Scope)](#4-strategy-engine-phase-1-scope)
5. [Risk Management (Phase 1 Scope)](#5-risk-management-phase-1-scope)
6. [Error Handling & Resilience](#6-error-handling--resilience)
7. [Testing Strategy](#7-testing-strategy)
8. [Rollout & Demo Plan](#8-rollout--demo-plan)
9. [Explicit Deferrals](#9-explicit-deferrals)

---

## 1. Project Structure & Cleanup

**Goal**: Transform the chaotic root directory (43 MQL5 files, 5 Python files) into an industry-standard layout.

### Structure
```
mql_01/
├── src/
│   ├── mql5/
│   │   ├── experts/           # Main EA files
│   │   │   └── AAT_Expert.mq5
│   │   ├── include/           # Shared headers
│   │   │   ├── AAT_Dashboard.mqh
│   │   │   ├── AAT_SocketClient.mqh
│   │   │   ├── AAT_JsonParser.mqh
│   │   │   ├── AAT_StrategyRegistry.mqh
│   │   │   └── AAT_TradingEngine.mqh
│   │   └── scripts/           # Setup/utility scripts
│   └── python/
│       ├── AAT_MainEngine.py
│       ├── AAT_StrategyMaster.py
│       ├── AAT_RiskManager.py
│       ├── AAT_DataAggregator.py
│       ├── AAT_Protocol.py     # Message protocol definitions
│       └── AAT_Config.py       # Centralized config
├── config/
│   ├── aat_config.json         # Runtime configuration
│   └── vault.json.enc          # Encrypted API keys
├── tests/
│   ├── test_bridge.py          # Python-side bridge tests
│   └── test_strategies.py      # Strategy unit tests
├── docs/
│   └── specs/                  # Design documents
├── scripts/
│   ├── setup_portable_python.bat
│   └── setup_python_env.ps1
├── _archive/                   # Legacy files (READ ONLY)
│   └── (all 43 legacy .mq5 files)
├── requirements.txt
├── README.md
└── CLAUDE.md
```

### Key Decisions
- **No versioned filenames in `src/`**: Version info lives in the standardized FOSS header (per spec AP20: `# Version: V3.1.0_20260606`)
- **`_archive/`**: All legacy files moved here for reference only — not part of the build
- **Centralized protocol/config**: `AAT_Protocol.py` and `AAT_Config.py` eliminate magic strings and hardcoded values

---

## 2. Socket Bridge Protocol

**Goal**: Reliable, low-latency, secure communication between MQL5 EA and Python Engine.

### Architecture
```
┌─────────────────────┐          TCP Socket (AES-256)          ┌─────────────────────┐
│     MQL5 EA         │◄────────────────────────────────────►│   Python Engine     │
│                     │                                        │                     │
│  OnTick:            │   1. HEARTBEAT (10s bidirectional)     │  Background:        │
│  - Collect OHLC     │   2. OHLC_PUSH (EA → Python)          │  - Data scraping    │
│  - Send to Python   │   3. ANALYSIS_REQUEST (EA → Python)   │  - Sentiment fetch  │
│  - Execute signals  │   4. CONSENSUS_RESPONSE (Python → EA)  │  - Prediction mkt   │
│  - Update dashboard │   5. RISK_CHECK (EA → Python)          │  - ML inference     │
│                     │   6. RISK_RESPONSE (Python → EA)       │                     │
└─────────────────────┘                                        └─────────────────────┘
```

### Message Format (JSON Envelope)

All messages follow this structure:
```json
{
  "type": "MESSAGE_TYPE",
  "symbol": "EURUSD",
  "timestamp": 1718400000,
  "payload": { ... }
}
```

### Message Types

| Type | Direction | Trigger | Payload |
|------|-----------|---------|---------|
| `PING` | Both | Every 10s | `{}` |
| `PONG` | Both | On PING | `{ uptime: 86400 }` |
| `OHLC_PUSH` | EA→Py | On new bar (any TF) | `{ tf: "M15", candles: [...] }` |
| `ANALYSIS_REQ` | EA→Py | On signal opportunity | `{ symbol, strategy: "all" }` |
| `CONSENSUS_RSP` | Py→EA | After analysis | `{ direction, confidence, strategies_fired: [...] }` |
| `RISK_CHECK` | EA→Py | Before trade execution | `{ symbol, direction, lots, entry_price }` |
| `RISK_RSP` | Py→EA | After risk evaluation | `{ approved, reason, adjusted_lots }` |

### Fallback Chain (Zero-Stub Guarantee)
1. Try persistent socket (5s timeout)
2. Switch to file-based IPC (`/tmp/aat_msg_*.json`)  
3. Retry socket every 30s; on recovery, resume & flush queue

### Security (Per Spec AP)
- **AES-256-CBC encryption** of payload (even on localhost)
- **Token authentication**: Shared secret derived from `vault.json` (never plaintext on disk)

---

## 3. Dashboard Architecture

**Goal**: Institutional-grade "Glass Cockpit" UI with zero performance impact.

### Layout (3-Tab System)
```
┌──────────────────────────────────────────────────────────────────────┐
│ [HEALTH] [LIVE ANALYTICS] [SETTINGS]              AAT v3.1.0  ♦ LIVE│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TAB 1: HEALTH & SAFETY                                             │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │ Symbol   │  M1  M5  │ M15 M30  │  H1  H4  │  D1 W1  │ CONSENSUS│
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤          │
│  │ EURUSD   │  ▲  ▼   │  ▲   ─  │  ─   ▲  │  ▲  ─  │ BUY (8) │
│  │ GBPUSD   │  ─  ▼   │  ▼   ▼  │  ▼   ▼  │  ─  ─  │ SELL (7)│
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
│                                                                      │
│  HEALTH: OK    HEARTBEAT: 10s    ENGINE LAT: 3ms    VaR: 1.2%      │
│  SPREAD: 0.8p  CANDLE T-: 2:34  P&L: +$42.50    REGIME: Trending │
│  DRAWDOWN: 2%  CORREL: 0.85    POLYMARK: Neutral  MODE: SCALP     │
│                                                                      │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ ⚠ ACTIVE SIGNAL: BUY EURUSD │ CONF: 85% │ STRATS: 4/5│           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                      │
│  TAB 2: LIVE ANALYTICS (expandable per-signal details)              │
│  TAB 3: SETTINGS (risk %, strategy toggles, trailing params)        │
│                                                                      │
│  STATUS BAR:  [●]Connected  │  Trades: 3  │  Win: 67%  │  Uptime: 4h│
└──────────────────────────────────────────────────────────────────────┘
```

### Technical Implementation
- **CCanvas rendering** (full control, low overhead, works inside MT5)
- **500ms throttling** (skip render if <500ms since last update - per spec AP26)
- **Eco-mode**: 1 FPS when chart hidden, 30 FPS when visible
- **Bitmap fonts** integrated (fallback to MT5 standard only if unavoidable)
- **Theme**: Cyber-Pro Dark (neon green/red on semi-transparent charcoal with animated pulse)

---

## 4. Strategy Engine (Phase 1 Scope)

**Goal**: Prove the full end-to-end pipeline with one working strategy.

### Strategy: Multi-TF Trend Consensus
A conservative, high-probability strategy demonstrating EA→Python→signal→execution flow.

#### Signal Components
| Component | Timeframe | Logic |
|-----------|-----------|-------|
| EMA Cross | M5 | 12/26 EMA crossover |
| RSI Zone  | H1 | RSI(14): <30 = OVERSOLD, >70 = OVERBOUGHT |
| ADX       | H1 | >25 = TRENDING, <20 = RANGING |
| VWAP      | M15 | Price vs session VWAP |
| Sentiment | D1  | Aggregated from FXStreet/ForexFactory/Polymarket |

#### Weighted Consensus Scoring
| Component | Weight | Signal Value |
|-----------|--------|--------------|
| EMA Cross (M5) | 30% | BUY=+1, SELL=-1, NEUTRAL=0 |
| RSI Zone (H1) | 20% | OVERSOLD=+1, OVERBOUGHT=-1, NEUTRAL=0 |
| ADX Strength | 20% | TRENDING=+0.5, RAGING=-0.5, WEAK=0 |
| VWAP Position | 15% | ABOVE=+0.5, BELOW=-0.5 |
| Sentiment | 15% | BULLISH=+1, BEARISH=-1, NEUTRAL=0 |
| **Threshold** | | **|score| ≥ 0.7 for execution** |

#### Data Flow
```
MQL5 EA OnTick()
  → Detect new bar on any TF
  → Push OHLC via socket (OHLC_PUSH)
  → Python Engine: calculate signals per TF
  → StrategyMaster: compute weighted consensus
  → RiskManager: evaluate trade safety (RISK_CHECK)
  → If approved: ExecuteTrade() via CTrade
  → Dashboard: update consensus cell + signal alert
```

---

## 5. Risk Management (Phase 1 Scope)

**Goal**: Minimum viable safeguards for demo trading. Advanced features (Kelly, correlation sizing) deferred.

### Phase 1 Risk Features
| Feature | Implementation | Purpose |
|---------|---------------|---------|
| **Position Sizing** | `Lot = (Equity × Risk%) / (ATR × PipsValue)` | Right-sized per symbol |
| **Max Drawdown Halt** | If floating DD > 5% equity → halt all trading | Prevent death spirals |
| **Daily Loss Limit** | If daily loss > 2% equity → stop for day | Cap worst-day exposure |
| **Consecutive Loss Pause** | After 3 losses → 30min cooldown | Prevent revenge trading |
| **Spread Filter** | If spread > 2× average → skip trade | Avoid bad fills |
| **Slippage Guard** | If estimated slippage > 10% of profit → abort | Per spec AP |
| **Cool-Down Mode** | Close all + notify + pause 4h on DD breach | Emergency brake |

### Pre-Trade Checklist (Flow)
1. EA wants to trade → sends `RISK_CHECK` to Python
2. Python evaluates all risk features above
3. Python returns `RISK_RSP: {approved, reason, adjusted_lots}`
4. If approved: EA executes trade at adjusted lot size
5. If rejected: EA logs reason, skips trade, continues monitoring

---

## 6. Error Handling & Resilience

**Goal**: "Treat capital preservation as job number one" (spec golden rule).

### Three-Layer Strategy
```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: PREVENT — Don't let errors happen                 │
│  - Input validation on all external data                    │
│  - Capability checks before every action                    │
│  - Pre-flight safety verification (heartbeat, time sync)    │
├─────────────────────────────────────────────────────────────┐
│  LAYER 2: DETECT — Know when errors happen instantly        │
│  - Bidirectional heartbeat (10s)                           │
│  - Data integrity checks (NaN, empty, stale timestamps)    │
│  - State reconciliation (positions, equity vs broker)      │
├─────────────────────────────────────────────────────────────┘
│  LAYER 3: RECOVER — Get back to safe state automatically    │
│  - Retry with exponential backoff (1s,2s,4s,8s,max30s)    │
│  - Fail-safe: move positions to break-even on critical err │
│  - Emergency force-close on unrecoverable errors           │
│  - Hot-swap to file-based fallback when socket fails      │
└─────────────────────────────────────────────────────────────┘
```

### Zero-Stub Retry Pattern (Applied Universally)
```python
def retry_with_backoff(op, max_att=5, base=1.0, max_delay=30.0):
    """Every external call gets ≥5 attempts with exponential backoff."""
    for i in range(max_att):
        try:
            return op()
        except Exception as e:
            if i == max_att - 1:
                log_critical(f"{op.__name__} failed after {max_att} attempts: {e}")
                raise  # or trigger emergency procedure
            delay = min(base * (2 ** i), max_delay)
            log_warning(f"Attempt {i+1} failed, retrying in {delay}s: {e}")
            time.sleep(delay)
```

### Concrete Coverage (Phase 1)
| Scenario | Detection | Response |
|----------|-----------|----------|
| Python engine crash | Heartbeat >30s timeout | Auto-switch to file-based IPC |
| Socket dropped | TCP exception | Reconnect with backoff; use file IPC during outage |
| Data feed stale | No new bar for 3× expected period | Pause trading, alert on dashboard |
| Broker rejects order | Trade return ≠ DONE | Log details; retry once after 5s, then halt |
| Equity spike/drop | >10% change in 60s | Emergency halt; force-close all to break-even |
| Indicator NaN/empty | Invalid signal from StrategyMaster | Skip cycle; log warning; continue |
| Disk full (logs) | Log write exception | Stop logging; alert; continue trading |
| Time clock skew | EA vs Python time >5s apart | Use server time only; log warning |
| Network partition | All socket attempts fail | Move SL to break-even on all positions; halt |

---

## 7. Testing Strategy

**Goal**: L99 certification — 99%+ confidence the system won't fail in production.

### Test Pyramid (Trading-Specific)
```
                    ╱  ╲      Live Demo (broker, market hours)
                   ╱    ╲     - Real market, zero real money
                  ╱ 4 wk ╲    - Catches: weird market data, broker quirks
                 ╱        ╲
                ╱──────────╲     Integration (MT5 + Python on same dev box)
               ╱            ╲   - All 7 message types
              ╱   2-3 days  ╲  - Heartbeat, fallback chain, state sync
             ╱                ╲
            ╱──────────────────╲   Unit Tests (per component)
           ╱                    ╲  - Python: 100% strategy logic, risk math
          ╱   ~50 tests, 2 days  ╲  - MQL5: 100% indicator calcs, signal registry
         ╱                        ╲
        ╱──────────────────────────╲
```

### Phase 1 Test Coverage Targets
| Component | Test Type | Target | Why |
|-----------|-----------|--------|-----|
| `AAT_Protocol.py` | Unit tests | 100% | Message correctness is critical path |
| `AAT_StrategyMaster.py` | Unit tests | 100% | Bad math = bad trades |
| `AAT_RiskManager.py` | Unit tests | 100% | Wrong lot size = blown account |
| `AAT_SocketClient.mqh` | Integration | 100% of types | Bridge failure = total system failure |
| End-to-end pipeline | Integration | All 7 types | Prove EA↔Python works |
| Heartbeat fallback | Integration | Verified <30s switch | No live trading without heartbeat |
| Demo dry-run | Manual | 1 week minimum | Real market conditions |

### 10 L99 Verification Tests (Phase 1 Must Pass)
1. Bridge survives Python crash → EA halts trading within 30s, no unprotected open trades  
2. File-based fallback works → EA receives consensus via file write within 60s  
3. All 11 timeframes (M1-MN) push correctly → Python receives matching bar data  
4. Consensus threshold blocks weak signals → Reject |score| < 0.7  
5. Position sizing returns zero when ATR is invalid → Never trade on bad data  
6. 3 consecutive losses trigger 30min cooldown → Verified via simulated trades  
7. 5% drawdown halts trading → Verified via mock equity drop  
8. Spread > 2× average aborts trade → Edge case: news spike moments  
9. AES-256 roundtrip → Message encrypts/decrypts byte-identical  
10. Watchdog kills stateless trades → Heartbeat >15s → all positions → break-even  

---

## 8. Rollout & Demo Plan

### Phase 1 Timeline (6-8 Weeks)
| Week | Deliverable | Gate Criteria |
|------|-------------|---------------|
| 1 | Project restructure + `_archive/` migration | Clean compile, all legacy files migrated |
| 2 | Socket bridge + AES-256 + heartbeat | All 7 message types pass integration tests |
| 3 | Dashboard (3-tab CCanvas) + 500ms throttle | Visual verification on demo chart |
| 4 | Python StrategyMaster + RiskManager | 100% unit test coverage |
| 5 | End-to-end integration on demo | All 10 L99 verification tests pass |
| 6-8 | Demo dry-run (1 symbol, 1 strategy, EURUSD) | Statistical significance + zero critical bugs |

### Demo Gates (Before Phase 2)
- ✓ 50+ trades taken with positive expectancy  
- ✓ Zero unhandled exceptions in 4 weeks of demo  
- ✓ Heartbeat verified <5s median latency  
- ✓ All risk halt scenarios (DD>5%, daily loss>2%, etc.) tested  
- ✓ Dashboard updates correctly reflect engine state  

---

## 9. Explicit Deferrals (Anti-Scope Creep)

**To maintain Phase 1 focus, these features are explicitly deferred**:

### Deferred to Phase 2
- News Straddle execution logic  
- Pyramid scaling system  
- Mean Reversion strategy  
- Breakout strategy  
- Multi-symbol coordination (6-10 symbols)  
- Correlation-adjusted position sizing  
- Kelly Criterion risk management  
- Symmetric heartbeat verification  

### Deferred to Phase 3  
- XGBoost consensus engine  
- FinBERT sentiment analysis  
- FAISS pattern matching  
- Monte Carlo simulation (pre-trade)  
- News scrapers with DNS/IP rotation  
- Shared memory DLL (custom C++ implementation)  
- Custom strategy slots in MT5 UI  
- Telegram & MT5 push hybrid alerting  

### Deferred to Phase 4  
- QuestDB + SQLite hybrid storage with sync service  
- Cross-terminal shared state synchronization  
- Reinforcement Learning for strategy weighting  
- Advanced backtesting & parameter optimization harness  
- Equity curve protection & volatility-based risk adjustment  
- Weekend Bayesian optimization (auto-retrain)  
- Decentralized dashboard sync via IPFS  

---

## APPROVAL

This document represents the **approved design for AAT Phase 1: The Bridge Builder**.  
Implementation proceeds only after written user approval of this spec.

**Next Step**: User reviews this spec → requests changes (if any) → approval → invoke `writing-plans` skill to create implementation plan.