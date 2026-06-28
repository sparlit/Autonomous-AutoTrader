import pandas as pd
from src.python.brains.base import BaseBrain, SignalPayload
class SwingMaster(BaseBrain):
    """Magic: 20010"""
    def __init__(self, name, ipc=None): super().__init__(name, ipc=ipc); self.magic = 20010
    async def process(self, data):
        h = data.get("ltf", [])
        if len(h) < 50: return None
        df = pd.DataFrame(h); e50 = df['c'].ewm(span=50).mean().iloc[-1]
        d = 1 if df['c'].iloc[-1] > e50 else -1
        return SignalPayload(symbol=data.get("s", "UNK"), timeframe=data.get("tf", 0), direction=d, confidence=0.7, strategy_name=self.name, magic=self.magic)
