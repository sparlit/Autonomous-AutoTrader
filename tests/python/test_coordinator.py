import pytest
import asyncio
import time
from src.python.hive.coordinator import HiveOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = HiveOrchestrator()
    assert orchestrator.ipc is not None
    assert orchestrator.brains is not None

@pytest.mark.asyncio
async def test_brain_swarm_spawn():
    orchestrator = HiveOrchestrator()
    orchestrator._spawn_brain_swarm()
    assert len(orchestrator.brains) > 0
    # Cleanup
    orchestrator.stop()
