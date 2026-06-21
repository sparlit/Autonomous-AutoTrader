import sys
import os
import asyncio
import logging
import psutil

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.python.hive.coordinator import HiveOrchestrator

def setup_os_optimization():
    """Pin the main supervisor to CPU 0."""
    p = psutil.Process(os.getpid())
    try:
        p.cpu_affinity([0])
        logging.info("Supervisor pinned to CPU 0")
    except Exception as e:
        logging.warning(f"OS Optimization failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s"
    )

    setup_os_optimization()

    logger = logging.getLogger("AAT_Main")
    logger.info("🌌 Launching Autonomous AutoTrader: Phoenix Ascendant")

    orchestrator = HiveOrchestrator()

    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        logger.info("Initiating Graceful Shutdown...")
        orchestrator.stop()
        logger.info("Phoenix Ascendant offline.")
