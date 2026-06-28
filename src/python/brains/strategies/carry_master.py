from typing import Any
import pandas as pd
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class CarryMaster(BaseBrain):
    """
    Carry/Position Trading Strategy.
    Alignment: D1 Trend + High Interest Differential (Simulated).
    Magic: 20002
    """
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20002
        # Simulated Carry Map (Positive = Long Carry)
        self.carry_bias = {"USDJPY": 1, "GBPUSD": -1, "EURUSD": -1, "AUDUSD": 1, "NZDUSD": 1}

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        symbol = data.get("s", "UNKNOWN")
        if not history or len(history) < 200: return None

        df = pd.DataFrame(history)
        ema_200 = df['c'].ewm(span=200).mean().iloc[-1]
        trend = 1 if df['c'].iloc[-1] > ema_200 else -1

        bias = self.carry_bias.get(symbol, 0)
        direction = 0
        if trend == bias and bias != 0:
            direction = bias # Carry-aligned trend

        return SignalPayload(
            symbol=symbol,
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.9 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
