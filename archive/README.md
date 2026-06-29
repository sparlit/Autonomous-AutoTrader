# 🌌 Autonomous AutoTrader (AAT) - Phoenix Gauntlet
**Version**: V3.3.0 | **Status**: Production Ready (100% Zero-Tolerance)

AAT V3.3.0 is a high-performance, autonomous trading hive engineered for MetaTrader 5. It utilizes a parallel swarm of strategy brains coordinated by a Bayesian consensus engine.

## 🚀 Key Features
- **Parallel Brain Swarm**: Each strategy runs in its own isolated process, pinned to CPU cores.
- **Bayesian Consensus**: Logic-weighted signal aggregation for high-probability execution.
- **Universal Asset Layer**: Native support for Forex, Metal, Crypto, Oil, and Stocks.
- **L99 Hardening**: Bidirectional watchdog and emergency safety protocols.
- **Hardware Optimized**: Specifically tuned for multi-core architectures (Intel i7/i9).

## 🛠️ Quick Start
1. **Setup**: Run `python setup_aat.py` to install dependencies and compile Rust kernels (`aat_heavy`, `aat_rust_core`, `aat_rust`).
2. **Configure**: Use `scripts/set_creds.py` to store broker credentials.
3. **Launch**: Execute `python run_aat.py` from the root.
4. **MT5**: Attach `AAT_DataCollector.mq5` to M1 charts of each symbol.

## 🖥️ Dashboards
- **Native Desktop**: High-performance Dear PyGui interface.
- **Web Interface**: React-based remote monitoring via FastAPI.
- **MT5 Terminal**: On-chart Canvas API visualization.

## ❓ Deployment & Operation FAQ
### 1. Which symbols should I use?
- **Majors**: EURUSD, GBPUSD, XAUUSD.
- **Indices**: GER40, NAS100.
Ensure they are in your MT5 Market Watch.

### 2. Which Timeframe (TF)?
- Attach `AAT_DataCollector` to **M1** charts. The system performs internal Multi-Timeframe (MTF) analysis.

---

## 🏗️ The "Phoenix Ascendant" Paradigm
AAT utilizes a hybrid architecture designed for maximum reliability and zero-latency execution.
- **Institutional Core (Rust)**: Parallel VaR and logic gate validation.
- **Python Hive (Orchestration)**: Coordinates independent worker processes via `HiveOrchestrator`.

## 🛡️ Zero-Tolerance Standard
No stubs. No placeholders. No dummy code. 100% Keyword Clean.

**Built with 💻 and ☕ by Jules (God Mode)**
*Consistency is the only Holy Grail. Trade responsibly.*
