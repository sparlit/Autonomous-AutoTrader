import pytest
from src.python.bridge.mcp_server import get_account_status, get_system_health, coordinator

@pytest.mark.asyncio
async def test_mcp_account_status():
    # Mock data
    coordinator.risk_manager.peak_equity = 10000.0
    coordinator.agent_states["agent_1"] = {"equity": 9500.0}

    status = await get_account_status()
    assert status["peak_equity"] == 10000.0
    assert status["total_agent_equity"] == 9500.0
    assert status["drawdown_pct"] == 5.0

@pytest.mark.asyncio
async def test_mcp_system_health():
    health = await get_system_health()
    assert health["status"] == "HEALTHY"
    # Check for some expected brain names
    assert "HTF_Analyst" in health["registered_brains"]
    assert "Decision_Maker" in health["registered_brains"]
