import sys
import os
import asyncio
import io
import logging
import psutil

# Add project root to sys.path
# File is in src/python/main_engine.py, root is ../../
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 10001: Force UTF-8 encoding for Windows Console to prevent "≡ƒîî" errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from scripts.pre_compile import pre_compile
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.security import CredentialManager

def setup_os_optimization():
    """Pin the main supervisor to CPU 0 if available."""
    p = psutil.Process(os.getpid())
    total_cores = psutil.cpu_count()
    try:
        if total_cores > 0:
            p.cpu_affinity([0])
            logging.info("Supervisor pinned to CPU 0")
    except Exception as e:
        logging.debug(f"OS Optimization failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s"
    )

    print("🌌 Launching Autonomous AutoTrader: V3.3.0")
    pre_compile()
    setup_os_optimization()

    logger = logging.getLogger("AAT_Main")
    logger.info("Starting Hive Orchestrator...")

    # 11055: Initialize Security Vault
    vault = CredentialManager()
    creds = vault.load_credentials()
    if creds:
        logging.info(f"Vault unlocked for Account: {creds.get('account')}")
    else:
        logging.warning("Vault is empty. Manual login required in MT5 or use CredentialManager.save_credentials()")

    orchestrator = HiveOrchestrator(credentials=creds)

    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        logger.info("Initiating Graceful Shutdown...")
        orchestrator.stop()
        logger.info("Phoenix offline.")
