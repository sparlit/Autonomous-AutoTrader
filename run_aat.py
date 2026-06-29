import asyncio
import logging
import sys
import io
from src.python.hive.coordinator import HiveOrchestrator

# 10000: Force UTF-8 Encoding for Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/aat_system.log")]
)

async def main():
    config = {"mode": "PROD", "version": "V3.3.0"}
    orchestrator = HiveOrchestrator(config)
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
