import pytest
from src.python.brains.consensus import MetaBrain
@pytest.mark.asyncio
async def test_meta():
    meta = MetaBrain("Test", threshold=0.1)
    # Mocking for test
    meta.required_count = 3
    for i in range(1, 4):
        res = await meta.process({"s": "EURUSD", "strategy_name": f"S{i}", "direction": 1, "confidence": 0.8})
        if i < 3: assert res is None
    assert res is not None
