import asyncio
from typing import Dict, Any, List
from fastmcp import FastMCP
from src.python.hive.coordinator import HiveCoordinator

mcp = FastMCP("Autonomous-AutoTrader")
coordinator = HiveCoordinator()

@mcp.tool()
async def get_account_status() -> Dict[str, Any]:
    """
    Get the current account status, including balance, equity, and drawdown.
    """
    peak = coordinator.risk_manager.peak_equity
    # Aggregate states from agents
    agents = coordinator.agent_states
    total_equity = sum(a.get("equity", 0) for a in agents.values())

    return {
        "peak_equity": peak,
        "total_agent_equity": total_equity,
        "active_agents": list(agents.keys()),
        "drawdown_pct": round((peak - total_equity) / peak * 100, 2) if peak > 0 else 0
    }

@mcp.tool()
async def list_active_trades(symbol: str = None) -> List[Dict[str, Any]]:
    """
    List all currently open trades, optionally filtered by symbol.
    """
    return await coordinator.ledger.get_active_trades_db(symbol)

@mcp.tool()
async def place_manual_trade(symbol: str, action: str, lots: float, sl_pts: int, tp_pts: int) -> Dict[str, Any]:
    """
    Manually signal a trade intent to the system.
    Note: This records intent; actual execution depends on an active MT5 agent.
    """
    if action not in ["BUY", "SELL"]:
        return {"status": "ERROR", "message": "Action must be BUY or SELL"}

    # In this system, AAT usually reacts to DP from MT5.
    # For a "manual" trade via MCP, we record the intent in the ledger.
    # The next time the agent for that symbol sends a DP, we could force-inject this.
    # However, for now, let's just record it as a PENDING trade.

    intent_id = await coordinator.ledger.record_intent(symbol, action, lots, 0, 0) # price/sl/tp calculated by risk manager usually
    return {"status": "SUCCESS", "intent_id": intent_id, "message": "Trade intent recorded. Agent synchronization required for execution."}

@mcp.tool()
async def get_system_health() -> Dict[str, Any]:
    """
    Get the health status of the AAT coordinator and its components.
    """
    return {
        "status": "HEALTHY",
        "registered_brains": list(coordinator.registry._brains.keys()),
        "active_agents_count": len(coordinator.agent_states),
        "news_safety": coordinator.risk_manager.is_news_safe(),
        "session_active": coordinator.risk_manager.is_session_active()
    }

async def initialize_coordinator():
    """Initialize the coordinator's database and background tasks."""
    await coordinator.ledger.init_db()
    coordinator.risk_manager.peak_equity = coordinator.ledger.get_cached_peak_equity()
    asyncio.create_task(coordinator.watchdog.run())
    asyncio.create_task(coordinator.context_brain.update_global_context())

# Initialize when module is loaded (FastMCP will run the loop)
# Note: FastMCP handles its own event loop when running.
# We'll use a startup hook if FastMCP supports it, or just await in tools.
