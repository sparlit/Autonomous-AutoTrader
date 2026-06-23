import multiprocessing
import pickle
import pytest
from src.python.hive.ipc import HiveIPC

def test_hive_ipc_picklable():
    """Verify that HiveIPC can be pickled for Windows 'spawn' compatibility."""
    ipc = HiveIPC()
    # Pre-create a queue to ensure proxy objects are in the state
    ipc.get_queue("test_stream")
    ipc.set_state("global_key", "global_value")

    # Pickle and unpickle
    pickled = pickle.dumps(ipc)
    unpickled_ipc = pickle.loads(pickled)

    # Check that proxies are still functional
    assert unpickled_ipc.get_state("global_key") == "global_value"

    # Check that manager and lock are removed in child state
    assert unpickled_ipc.manager is None
    assert unpickled_ipc._lock is None

    # Check that existing queue is accessible
    q = unpickled_ipc.get_queue("test_stream")
    assert q is not None

    # Check that creating NEW queue in child fails (as expected by design)
    with pytest.raises(RuntimeError) as excinfo:
        unpickled_ipc.get_queue("new_stream")
    assert "Parent must pre-initialize" in str(excinfo.value)
