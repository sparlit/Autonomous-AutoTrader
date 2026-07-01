import asyncio
import ujson as json
import time
from src.python.hive.ipc import HiveIPC

async def flatten():
    ipc = HiveIPC()
    # Send Global Close All signal via the Orchestrator stream
    # The Orchestrator routes EXECUTION_ORDER to the Bridge Server
    order = {
        "type": "EXECUTION_ORDER",
        "t": "DEC",
        "s": "GLOBAL",
        "act": "MGMT",
        "mgmt": "CLOSE_ALL",
        "reason": "EMERGENCY_DRAWDOWN_FLATTEN"
    }
    ipc.xadd("stream:orchestrator", order)
    print("🚀 Emergency CLOSE_ALL command dispatched to HiveOrchestrator.")

if __name__ == "__main__":
    asyncio.run(flatten())
