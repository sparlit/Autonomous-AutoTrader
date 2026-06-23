import asyncio
from typing import Dict, Any, List
from fastmcp import FastMCP
from src.python.hive.coordinator import HiveCoordinator

mcp = FastMCP("Autonomous-AutoTrader")
coordinator = HiveCoordinator()

@mcp.tool()
async def get_account_status() -> Dict[str, Any]:
    """
    Get current account status. Magic: 10001
    """
    peak = coordinator.risk_manager.peak_equity
    agents = coordinator.agent_states
    total_equity = sum(a.get("equity", 0) for a in agents.values())

    return {
        "peak_equity": peak,
        "total_agent_equity": total_equity,
        "active_agents": list(agents.keys()),
        "drawdown_pct": round((peak - total_equity) / peak * 100, 2) if peak > 0 else 0,
        "m_id": 1001
    }

@mcp.tool()
async def list_active_trades(symbol: str = None) -> List[Dict[str, Any]]:
    """
    List active trades. Magic: 10002
    """
    return await coordinator.ledger.get_active_trades_db(symbol)

@mcp.tool()
async def place_manual_trade(symbol: str, action: str, lots: float, sl_pts: int, tp_pts: int) -> Dict[str, Any]:
    """
    Record manual intent. Magic: 10003
    """
    if action not in ["BUY", "SELL"]:
        return {"status": "ERROR", "message": "Action must be BUY or SELL", "m_id": 1003}

    intent_id = await coordinator.ledger.record_intent(symbol, action, lots, 0, 0)
    return {"status": "SUCCESS", "intent_id": intent_id, "message": "Intent recorded.", "m_id": 1003}

@mcp.tool()
async def get_system_health() -> Dict[str, Any]:
    """
    Get system health. Magic: 10004
    """
    return {
        "status": "HEALTHY",
        "registered_brains": list(coordinator.registry._brains.keys()),
        "active_agents_count": len(coordinator.agent_states),
        "news_safety": coordinator.risk_manager.is_news_safe(),
        "session_active": coordinator.risk_manager.is_session_active(),
        "m_id": 1004
    }

async def initialize_coordinator():
    """Initialize coordinator components. Magic: 10005"""
    await coordinator.ledger.init_db()
    coordinator.risk_manager.peak_equity = coordinator.ledger.get_cached_peak_equity()
    asyncio.create_task(coordinator.watchdog.run())
    asyncio.create_task(coordinator.context_brain.update_global_context())
