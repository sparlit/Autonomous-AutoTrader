# 🧠 AAT Institutional Memory (V3.3.0)

## Core Architectural Patterns
- **Parallel Swarm**: The system decouples strategies into independent OS processes to bypass the Python GIL and leverage multi-core i7 hardware. Each brain is pinned to a specific core using CPU affinity.
- **Bayesian MetaBrain**: Replaces simple signal averaging with a reliability-weighted posterior probability calculation. Strategies that perform better in the current regime gain more voting power.
- **Asset Normalization Layer**: A centralized arbiter that maps broker-specific symbols to universal tickers and normalizes lot-sizes/tick-values for Forex, Crypto, Metal, and Stocks.
- **L99 Watchdog**: A bidirectional safety heartbeat that monitors the link between MetaTrader 5 and the Python hive. Loss of pulse triggers an immediate "Safety Flatten" protocol.

## Zero-Tolerance Protocols
- No stubs or placeholders are permitted in the `src/` directory.
- All abstract methods must provide functional logging or be fully implemented.
- Every logic path must have a unique institutional Magic Number for deterministic tracking.

## Deployment Procedure
- Use `setup_aat.py` for one-click environment initialization and Rust kernel compilation.
- Credentials must be stored in the DPAPI-encrypted vault via `scripts/set_creds.py`.
