import pandas as pd
import datetime
from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class DayMaster(BaseBrain):
    """
    Institutional Day Trading (London ORB).
    Focus: Breakout of 07:00-08:00 UTC range.
    Magic: 20201
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.magic = 20201

    async def process(self, data: dict) -> Optional[SignalPayload]:
        history = data.get("history", [])
        if not history or len(history) < 60: return None

        df = pd.DataFrame(history)
        df['dt'] = pd.to_datetime(df['t'], unit='s', utc=True)

        # Opening Range: 07:00 - 08:00 UTC
        today = df['dt'].iloc[-1].date()
        orb_start = datetime.datetime.combine(today, datetime.time(7, 0), datetime.UTC)
        orb_end = datetime.datetime.combine(today, datetime.time(8, 0), datetime.UTC)

        orb_df = df[(df['dt'] >= orb_start) & (df['dt'] <= orb_end)]
        if orb_df.empty: return None

        range_h = orb_df['h'].max()
        range_l = orb_df['l'].min()

        curr_price = df['c'].iloc[-1]
        curr_time = df['dt'].iloc[-1].time()

        direction = 0
        # Only trade London/NY sessions
        if datetime.time(8, 1) <= curr_time <= datetime.time(16, 0):
            if curr_price > range_h: direction = 1
            elif curr_price < range_l: direction = -1

        return SignalPayload(
            symbol=data.get("s", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=direction,
            confidence=0.6,
            strategy_name=self.name,
            magic=self.magic
        )
