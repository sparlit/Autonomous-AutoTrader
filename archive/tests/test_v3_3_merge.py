import pytest
import asyncio
import os
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.ipc import HiveIPC

@pytest.mark.asyncio
async def test_v3_3_architecture_integrity():
    """Verify that the merged orchestrator follows the V3.3.0 swarm pattern."""
    orchestrator = HiveOrchestrator()
    assert hasattr(orchestrator, "registry")
    assert hasattr(orchestrator, "watchdog")
    assert hasattr(orchestrator, "_spawn_brain_swarm")
    assert hasattr(orchestrator, "brains")

    # In some environments, the decorator or mocking might cause issues.
    # We ensure we are awaiting a coroutine.
    await orchestrator._spawn_brain_swarm()

    assert len(orchestrator.registry._brains) >= 18
    assert len(orchestrator.brains) >= 18

    # Verify MetaBrain is present
    assert "MetaBrain" in orchestrator.registry._brains

    await orchestrator.stop()

@pytest.mark.asyncio
async def test_ipc_stability():
    """Verify IPC is shared correctly between orchestrator and brains."""
    ipc = HiveIPC()
    ipc.clear_memory()
    ipc.set_state("test_key", "test_val")
    assert ipc.get_state("test_key") == "test_val"
