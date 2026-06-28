import psutil
import logging
from typing import Dict, Any, List
logger = logging.getLogger("AAT_HardwareAnalyst")
class HardwareAnalyst:
    """10150: Hardware Analyst. Magic: 10150"""
    def __init__(self, db_path="audit_records.db"):
        self.logical_cores = psutil.cpu_count(logical=True)
        self.total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    def get_optimized_affinity_map(self, num_brains: int) -> Dict[int, List[int]]:
        """10152: Affinity Map. Magic: 10152"""
        mapping = {}
        available = list(range(2, self.logical_cores)) if self.logical_cores > 2 else [0]
        for i in range(num_brains): mapping[i] = [available[i % len(available)]]
        return mapping
    def log_capabilities(self):
        """10155: Log stats. Magic: 10155"""
        logger.info(f"🚀 Hardware: {self.logical_cores} Cores | {self.total_ram_gb}GB RAM")
