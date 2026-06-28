from typing import Any
import pandas as pd
import datetime
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class ICTKillzone(BaseBrain):
    """Magic: 20006"""
    def __init__(self, name: str, ipc: Any = None):
        super().__init__(name, ipc=ipc)
        self.magic = 20006

    async def process(self, data: dict) -> Optional[SignalPayload]:
        """Method Logic. Magic: 20502"""
        history = data.get("history", [])
        if not history or len(history) < 20: return None

        df = pd.DataFrame(history)
        # Institutional Assumption: 't' is UNIX UTC
        last_dt = datetime.datetime.fromtimestamp(df['t'].iloc[-1], datetime.UTC)
        last_time = last_dt.time()

        # NY Open Killzone: 12:00 - 15:00 UTC
        is_ny_killzone = (datetime.time(12, 0) <= last_time <= datetime.time(15, 0))

        direction = 0
        if is_ny_killzone:
            # Reversal logic at session extreme
            if df['c'].iloc[-1] >= df['h'].max(): direction = -1
            elif df['c'].iloc[-1] <= df['l'].min(): direction = 1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.5 if direction != 0 else 0.0,
            strategy_name=self.name,
            magic=self.magic
        )
