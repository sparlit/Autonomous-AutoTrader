import psutil
import logging
import os
import sqlite3
import ujson as json
from typing import Dict, Any, List

logger = logging.getLogger("AAT_HardwareAnalyst")

class HardwareAnalyst:
    """10150: System Performance and Capability Detection."""
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path
        self.logical_cores = psutil.cpu_count(logical=True)
        self.physical_cores = psutil.cpu_count(logical=False)
        self.total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        self.cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 0.0

    def get_system_report(self) -> Dict[str, Any]:
        """Generate a full capability report."""
        capacity_score = (self.logical_cores * 0.5) + (self.total_ram_gb * 0.5)
        # 10151: Classification of machine tier
        tier = "INSTITUTIONAL" if capacity_score > 15 else ("PROFESSIONAL" if capacity_score > 8 else "STANDARD")

        return {
            "logical_cores": self.logical_cores,
            "physical_cores": self.physical_cores,
            "ram_gb": self.total_ram_gb,
            "cpu_max_freq": self.cpu_freq,
            "tier": tier,
            "capacity_score": capacity_score,
            "is_hyperthreaded": self.logical_cores > self.physical_cores
        }

    def get_optimized_affinity_map(self, num_brains: int) -> Dict[int, List[int]]:
        """
        10152: Distribute brains across cores, leaving room for OS and MT5.
        Strategy: Reserve Core 0 for Supervisor, Core 1 for Orchestrator.
        Distribute remaining brains across Cores 2 to N-1.
        """
        mapping = {}
        # Core 0: Supervisor (handled in main_engine.py)
        # Core 1: Orchestrator (handled in coordinator.py)

        available_cores = list(range(2, self.logical_cores))
        if not available_cores:
            # Fallback for low-core systems
            return {i: [0] for i in range(num_brains)}

        for i in range(num_brains):
            # 10153: Round-robin assignment with pinning
            core_idx = available_cores[i % len(available_cores)]
            mapping[i] = [core_idx]

        return mapping

    def log_capabilities(self):
        report = self.get_system_report()
        logger.info(f"🚀 Hardware Detected: {report['logical_cores']} Cores | {report['ram_gb']}GB RAM | Tier: {report['tier']}")

        # 10155: Persist capabilities to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS system_capabilities (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute("INSERT OR REPLACE INTO system_capabilities (key, value) VALUES (?, ?)", ("hardware_report", json.dumps(report)))
        except Exception as e:
            logger.error(f"Failed to persist hardware report: {e}")

        if report['logical_cores'] < 8:
            logger.warning("⚠️ System below Institutional specs. Performance may be degraded.")
