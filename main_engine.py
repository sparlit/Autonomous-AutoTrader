# Version: V3.1.0-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
from core.orchestrator import PhoenixOrchestrator

if __name__ == "__main__":
    orchestrator = PhoenixOrchestrator()
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        orchestrator.stop()
