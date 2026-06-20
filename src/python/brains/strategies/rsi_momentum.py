from typing import Optional
from src.python.brains.base import BaseBrain, SignalPayload

class RSIMomentum(BaseBrain):
    async def process(self, data: dict) -> Optional[SignalPayload]:
        """
        Generate a trading signal from the provided market data.

        Parameters:
            data (dict): Dictionary containing market data. Expected keys are 'symbol' (defaults to "UNKNOWN") and 'tf' for timeframe (defaults to 0).

        Returns:
            SignalPayload: Signal payload containing the trading signal information.
        """
        return SignalPayload(
            symbol=data.get("symbol", "UNKNOWN"),
            timeframe=data.get("tf", 0),
            direction=-1, # Mock SELL
            confidence=0.6,
            strategy_name="RSI_Momentum"
        )
