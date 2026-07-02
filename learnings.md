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
