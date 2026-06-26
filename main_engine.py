# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
import logging
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import PhoenixOrchestrator

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s"
    )

    orchestrator = PhoenixOrchestrator()
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        logging.info("Initiating Graceful Shutdown...")
        orchestrator.stop()
        logging.info("Phoenix Ascendant offline.")
