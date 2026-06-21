import sys
import os
import asyncio
import logging
import threading
import uvicorn

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.python.hive.coordinator import HiveCoordinator
from src.python.bridge.dashboards.web_server import app as web_app
from src.python.bridge.dashboards.native_gui import NativeDashboard

def run_web_dashboard():
    """Magic: 10006"""
    uvicorn.run(web_app, host="0.0.0.0", port=8080, log_level="warning")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    coordinator = HiveCoordinator()

    # 1. Start Native GUI in background thread
    gui = NativeDashboard()
    gui.start_async()

    # 2. Start Web Dashboard in background thread
    web_thread = threading.Thread(target=run_web_dashboard, daemon=True)
    web_thread.start()

    # 3. Main Event Loop for Coordinator
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        print("\n🦅 Phoenix Ascendant: Orderly Shutdown.")
