import sys
import os
import asyncio
import io

# 10001: Force UTF-8 encoding for Windows Console to prevent "≡ƒîî" errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import logging
import psutil
from pre_compile import pre_compile

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
        logging.warning(f"OS Optimization failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s"
    )

    print("🌌 Launching Autonomous AutoTrader: Phoenix Ascendant")
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
        logger.info("Phoenix Ascendant offline.")
