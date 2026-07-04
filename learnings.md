# Learnings - Institutional Zero-Tolerance Upgrade

## Architectural Patterns
- **Strict Vetting Chain:** Signals are now routed from Brains -> Orchestrator -> RiskBrain -> ExecutionBrain. This allows for mandatory cross-brain vetting (e.g., trend confirmation) even for signals generated internally by the PositionManager.
- **Shared State Management:** Using IPC (HiveIPC) to synchronize SL levels across multiple independent trades for the same symbol/direction ensures a unified institutional risk profile.
- **Bayesian Reliability Tuning:** The Learning Loop in MetaBrain demonstrates a pattern for self-correcting systems where performance metrics (win rate) directly influence decision thresholds (prior weights).

## Dashboard Witnessing
- **Glass-Box Principle:** Real-time visibility into internal brain metrics (Bayesian confidence) and "veto" reasons significantly improves operator trust in autonomous systems.
- **Hardware Telemetry:** Displaying logical/physical cores and system tier in the dashboard provides immediate context for the scaling and performance expectations of the brain swarm.

## MQL5-Python Sync
- **Enriched Telemetry:** Streaming MTF data and ATR on every tick is essential for high-fidelity risk calculation in Python. The sequence numbering (seq) ensures data integrity across the socket bridge.

## Stability & Migration
- **Self-Healing Schema:** Implementing automated migration in  (using ) is critical for preventing runtime "no such column" errors when the logic evolves faster than the database file.
- **DPAPI Resilience:** In institutional Windows environments,  is mandatory for DPAPI security. Added logic to detect platform-specific mismatches and provide logged warnings.

## Stability & Migration
- **Self-Healing Schema:** Implementing automated migration in `init_db` (using `PRAGMA table_info`) is critical for preventing runtime "no such column" errors when the logic evolves faster than the database file.
- **DPAPI Resilience:** In institutional Windows environments, `pywin32` is mandatory for DPAPI security. Added logic to detect platform-specific mismatches and provide logged warnings.

## Indentation and Syntax Resilience
- **Indentation Sensitivity:** Python is extremely sensitive to indentation. When programmatically editing files (e.g., using  or ), it is safer to rewrite entire methods or classes to ensure consistent spacing, rather than replacing single lines which might introduce mismatches.
- **Verification via Compilation:** Running `python3 -m compileall <file>` is a quick way to catch syntax/indentation errors without having to run the entire system.

## Indentation and Syntax Resilience
- **Indentation Sensitivity:** Python is extremely sensitive to indentation. When programmatically editing files (e.g., using `sed` or `cat <<EOF`), it is safer to rewrite entire methods or classes to ensure consistent spacing, rather than replacing single lines which might introduce mismatches.
- **Verification via Compilation:** Running 'python3 -m compileall <file>' is a quick way to catch syntax/indentation errors without having to run the entire system.

## Zero-Tolerance Execution Resilience
- **Atomic Trading Locks:** Using an IPC-level atomic lock (`acquire_trading_lock`) is the most reliable way to prevent race conditions and duplicate orders in a high-concurrency multi-process brain architecture.
- **Multi-Layer Vetting:** Implementing vetting checks at three distinct levels (Generation, Risk-Vetting, and MQL5-Bridge) creates a "Zero-Tolerance" environment where technical glitches (like 0 SL/TP) cannot result in invalid market orders.
- **Profit-Relative Scaling:** Calculating profit in USD using TickValue and TickSize before scaling ensures that the system only adds risk to positions that have established a meaningful profit margin, adhering to institutional capital preservation rules.
### IPC State Preservation (V3.3.0)
- **Problem:** multiprocessing.Lock and other manager proxies are often lost or set to None during pickling if they are explicitly deleted in `__getstate__`.
- **Solution:** Preserving these proxies in `__getstate__` allows the child process to reconstruct them successfully.
- **Pattern:** Parent processes should explicitly initialize MUST-HAVE streams (like `stream:orchestrator`) before spawning children to ensure proxies are valid in the swarm.
### CLI Signature Stability (V3.3.0)
- **Problem:** Updating the Orchestrator's internal logic can lead to signature mismatches with the supervisor CLI (`aat.py`) if optional arguments are not handled correctly.
- **Solution:** Always ensure that core orchestrator classes support optional `credentials` or `config` injections to maintain backward compatibility with the bootloader.
### NoneType Hardening (V3.3.0)
- **Problem:** Data arriving from MT5 can occasionally contain `null` (None) values for prices or ATR if the symbol is not fully initialized, leading to crash-inducing arithmetic errors.
- **Solution:** Implement a "Strict Float" pattern in the MarketDataBrain and Orchestrator, where all inputs are explicitly cast via `float(val or 0.0)`.
- **Pattern:** Always check for zero prices (bid/ask) before calculating mid-prices or P&L to prevent division by zero or nonsensical trading decisions.
### Dashboard Activation (V3.3.0)
- **Problem:** The Web and Native dashboards were correctly implemented but never explicitly launched by the coordinator.
- **Solution:** Integrated dashboard instantiation and lifecycle management directly into the HiveOrchestrator's run/stop sequence.
- **Pattern:** Dashboards should be treated as essential system components and launched as independent processes before brain initialization.
