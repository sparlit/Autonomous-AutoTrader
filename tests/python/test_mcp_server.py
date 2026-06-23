import pytest
import asyncio
from src.python.bridge.mcp_server import get_account_status, get_system_health, orchestrator

@pytest.mark.asyncio
async def test_mcp_account_status():
    # Verify we can call the tool and it returns a dict
    status = await get_account_status()
    assert isinstance(status, dict)
    assert "equity" in status
    assert "drawdown_pct" in status

@pytest.mark.asyncio
async def test_mcp_system_health():
    health = await get_system_health()
    assert isinstance(health, dict)
    assert "status" in health
