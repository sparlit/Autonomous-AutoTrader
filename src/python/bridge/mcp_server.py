import asyncio
import logging
from typing import Dict, Any, List
from fastmcp import FastMCP
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.ipc import get_ipc

logger = logging.getLogger("AAT_MCP")
mcp = FastMCP("Autonomous-AutoTrader")
orchestrator = HiveOrchestrator()
ipc = get_ipc()

@mcp.tool()
async def get_account_status() -> Dict[str, Any]:
    """
    Get current account status. Magic: 10001
    """
    stats = ipc.get_state("account_stats", {})
    return {
        "equity": stats.get("equity", 0.0),
        "drawdown_pct": stats.get("drawdown", 0.0),
        "active_symbol": stats.get("s", "N/A"),
        "m_id": 1001
    }

@mcp.tool()
async def get_system_health() -> Dict[str, Any]:
    """
    Get system health. Magic: 10004
    """
    engine = ipc.get_state("engine_stats", {})
    return {
        "status": engine.get("status", "INITIALIZING"),
        "msgs_rx": engine.get("msgs_rx", 0),
        "active_clients": engine.get("active_clients", 0),
        "m_id": 1004
    }

async def initialize_coordinator():
    """Start the orchestrator. Magic: 10005"""
    asyncio.create_task(orchestrator.run())
