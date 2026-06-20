from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class ADXTrend(BaseBrain):
    async def process(self, data: dict) -> Optional[SignalPayload]:
        """
        Create a signal payload from market data.
        
        Constructs a SignalPayload by extracting symbol and timeframe from the input data,
        with placeholder values for direction and confidence.
        
        Parameters:
            data (dict): Dictionary containing "symbol" and "tf" keys (defaults to
                "UNKNOWN" and 0 respectively if missing).
        
        Returns:
            SignalPayload: A signal payload with symbol and timeframe from input data.
        """
        return SignalPayload(
            symbol=data.get("symbol", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=0, # Mock NEUTRAL
            confidence=0.0,
            strategy_name="ADX_Trend"
        )
