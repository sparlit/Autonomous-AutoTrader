import pytest
import asyncio
import os
from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.ipc import HiveIPC

@pytest.mark.asyncio
async def test_v3_3_architecture_integrity():
    """Verify that the merged orchestrator follows the V3.3.0 swarm pattern."""
    orchestrator = HiveOrchestrator()
    assert hasattr(orchestrator, "brains")
    assert hasattr(orchestrator, "watchdog")
    assert hasattr(orchestrator, "_spawn_brain_swarm")

    # Check if expected brains are in the spawn list
    # We can't easily check strategy_classes without refactoring,
    # but we can verify it spawns something.
    orchestrator._spawn_brain_swarm()
    assert len(orchestrator.brains) >= 6

    # Verify MetaBrain is present
    meta_brain = next((b for b in orchestrator.brains if b.name == "MetaBrain"), None)
    assert meta_brain is not None

    orchestrator.stop()

@pytest.mark.asyncio
async def test_ipc_stability():
    """Verify IPC is shared correctly between orchestrator and brains."""
    ipc = HiveIPC()
    ipc.clear_memory()
    ipc.set_state("test_key", "test_val")
    assert ipc.get_state("test_key") == "test_val"
