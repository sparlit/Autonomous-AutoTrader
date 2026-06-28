import sys
import os
import asyncio
import io
import logging
import psutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path: sys.path.insert(0, ROOT_DIR)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from scripts.pre_compile import pre_compile
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.security import CredentialManager

def setup_os_optimization():
    p = psutil.Process(os.getpid())
    try: p.cpu_affinity([0])
    except Exception as e: logging.debug(f"OS Optimization failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s")
    print("🌌 Launching Autonomous AutoTrader: Phoenix Gauntlet")
    pre_compile()
    setup_os_optimization()
    creds = CredentialManager().load_credentials()
    orchestrator = HiveOrchestrator(credentials=creds)
    try: asyncio.run(orchestrator.run())
    except KeyboardInterrupt: orchestrator.stop()
