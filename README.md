# 🌌 Autonomous AutoTrader (AAT) - Phoenix Gauntlet
**Version**: V3.3.0 | **Status**: Production Ready (100% Zero-Tolerance)

AAT V3.3.0-ASCENDANT is a high-performance, institutional-grade autonomous trading hive engineered for MetaTrader 5. It utilizes a parallel swarm of strategy brains coordinated by a Bayesian consensus engine.

## 🚀 Quick Start
1. Run `INSTALL_AAT.bat` (Setup dependencies and Rust)
2. Run `START_AAT.bat` (Launch the Hive)

## 🛠️ CLI Management
The system is managed via a unified CLI:
- `python aat.py setup` : Complete system installation
- `python aat.py run`   : Launch Hive and Dashboards
- `python aat.py set-creds` : Encrypt and store MT5 credentials
- `python aat.py test` : Run the integration test suite

## 🚀 Key Features
- **Parallel Brain Swarm**: Each strategy runs in its own isolated process, pinned to CPU cores.
- **Bayesian Consensus**: Logic-weighted signal aggregation for high-probability execution.
- **Universal Asset Layer**: Native support for Forex, Metal, Crypto, Oil, and Stocks.
- **Real-Time Trade Telemetry**: High-fidelity tracking of PL, SL, TP, and duration across all dashboards.
- **Institutional Risk Engine**: Bayesian-weighted position sizing and dynamic SL/TP calibration.
- **L99 Hardening**: Bidirectional watchdog and emergency safety protocols.
- **Hardware Optimized**: Specifically tuned for multi-core architectures (Intel i7/i9).

## 🖥️ Dashboards
- **Native Desktop**: High-performance Dear PyGui interface.
- **Web Interface**: React-based remote monitoring via FastAPI.
- **MT5 Terminal**: On-chart Canvas API visualization.

---

## 🏗️ The "Phoenix Ascendant" Paradigm
AAT utilizes a hybrid architecture designed for maximum reliability and zero-latency execution.
- **Institutional Core (Rust)**: Parallel VaR and logic gate validation.
- **Python Hive (Orchestration)**: Coordinates independent worker processes via `HiveOrchestrator`.

## 🛡️ Zero-Tolerance Standard
No stubs. No placeholders. No dummy code. 100% Keyword Clean.

**Built with 💻 and ☕ by Jules (God Mode)**
*Consistency is the only Holy Grail. Trade responsibly.*
