import asyncio
import logging
import sys
import io
import os
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.security import CredentialManager

# 10000: Force UTF-8 Encoding for Windows Console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if not os.path.exists("logs"): os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/aat_system.log")]
)

async def main():
    logger = logging.getLogger("AAT_Main")
    logger.info("🌌 Launching Autonomous AutoTrader: Phoenix Gauntlet V3.3.0")

    # Initialize Security Vault
    vault = CredentialManager()
    creds = vault.load_credentials()

    orchestrator = HiveOrchestrator(credentials=creds)
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Initiating Graceful Shutdown...")
        orchestrator.stop()
        logger.info("Phoenix Gauntlet offline.")

if __name__ == "__main__":
    asyncio.run(main())
