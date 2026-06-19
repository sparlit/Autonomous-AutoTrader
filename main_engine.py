import sys
import os
import asyncio
import logging

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.python.hive.coordinator import HiveCoordinator

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    coordinator = HiveCoordinator()
    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        print("\nShutting down Hive...")
