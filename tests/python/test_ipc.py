import pytest
import asyncio
import time
from src.python.hive.ipc import get_ipc

@pytest.mark.asyncio
async def test_ipc_state_sharing():
    ipc = get_ipc()
    ipc.set_state("test_key", "test_value")
    # Small sleep for manager sync if needed, though dict is usually immediate
    assert ipc.get_state("test_key") == "test_value"

    all_state = ipc.get_all_state()
    assert "test_key" in all_state
    assert all_state["test_key"] == "test_value"

@pytest.mark.asyncio
async def test_ipc_queue_emulation():
    ipc = get_ipc()
    stream = "test_stream_final"
    data = {"payload": '{"test": "data"}'}

    ipc.xadd(stream, data)

    # xread returns List[Tuple[stream_name, List[Tuple[msg_id, data]]]]
    results = ipc.xread({stream: "0"}, count=1)

    assert len(results) == 1
    assert results[0][0] == stream
    assert results[0][1][0][1][b"payload"] == '{"test": "data"}'
