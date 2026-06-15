# 🏗️ PROPOSED ARCHITECTURE: AAT "PERFECT STRUCTURE"
**Architect**: Jules (God Mode Mode)
**Vision**: A Modular, Event-Driven Microkernel for Autonomous Trading

## 1. Directory Hierarchy (Industry Standard)
```text
/
├── .github/              # CI/CD Workflows
├── config/               # Unified Configuration (JSON/YAML)
│   ├── main_config.json  # Strategy & Risk parameters
│   └── symbols.json      # Symbol-specific contexts
├── docs/                 # Refined Documentation
├── scripts/              # Setup, Installation, & Maintenance
├── src/                  # Source Code
│   ├── mql5/             # MetaTrader 5 Implementation
│   │   ├── Experts/      # AAT_Expert.mq5
│   │   ├── Include/      # Core Libraries (AAT_Socket, AAT_Dashboard, etc.)
│   │   └── Scripts/      # Utility scripts for MT5
│   └── python/           # The "Brain" (Python Engine)
│       ├── core/         # Microkernel / Event Bus
│       ├── strategies/   # Strategy Plugins (Plug-in architecture)
│       ├── risk/         # Risk Management Engine
│       ├── bridge/       # TCP/IPC Server
│       └── data/         # Ingestion & Normalization
├── tests/                # Unified Test Suite
│   ├── python/           # Pytest suite
│   └── mql5/             # MQL5 Unit tests
├── requirements.txt      # Comprehensive Python dependencies
└── audit_records.db      # SQLite Persistence (Audit Trail)
```

## 2. Core Architectural Pillars

### 2.1 The Hybrid Strategy Kernel
To resolve the **Consensus vs. Sequential** conflict:
- **Architecture**: A "Pipeline" model.
- **Stage 1: Filters (Sequential)** - Hard vetos (Spread, News, Time).
- **Stage 2: Strategy Voting (Consensus)** - Each strategy emits a vote (-1, 0, 1) and a confidence score.
- **Stage 3: Decision Logic** - Aggregates votes into a final action.

### 2.2 Event-Driven Bridge (Zero Latency)
- **Transport**: Local TCP Sockets (Asyncio).
- **Format**: Protobuf or Minified JSON for speed.
- **Resilience**: Heartbeat-based "Dead Man Switch" in MQL5 that closes positions or moves to break-even if Python latency exceeds 500ms.

### 2.3 Resource-Optimized "Regime"
To resolve the **Hardware vs. Stack** conflict:
- **Default**: SQLite for local persistence (zero-overhead).
- **Optional**: Redis/Postgres only enabled via config if `Environment == 'Production_Institutional'`.
- **Local Engine**: Direct memory caching for 4GB-8GB RAM compatibility.

### 2.4 Multi-Symbol "Agent" Model
- Instead of one chart instance, the Python engine acts as a **Coordinator**.
- Each MT5 Chart Instance runs a "Slim Agent" EA.
- All agents report to the single Python Brain for global risk/correlation management.

## 3. The "Zero Stub" Implementation Path
- Every week of the plan must end with a **Functional Integration Gate**.
- No "stubs" allowed in the `main` branch. If a feature isn't implemented, the system skips it gracefully rather than using a placeholder.

---
## 4. Next Steps
1. **Approve Architecture**: User feedback on this structure.
2. **Restructure Disk**: Physically move/rename files to match.
3. **Synthesis**: Begin building `src/python/core/event_bus.py`.
