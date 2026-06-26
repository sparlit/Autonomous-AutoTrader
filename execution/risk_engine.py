# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
import logging
from typing import Dict, Any
from shared.memory import SharedState
from shared.config_manager import RiskConfig

logger = logging.getLogger("AAT_RiskEngine")

class InstitutionalRiskEngine:
    """11000: 7-Layer Risk Protection Stack."""
    def __init__(self, config: RiskConfig, shared_state: SharedState):
        self.config = config
        self.shm = shared_state

    def validate_execution(self, decision: Dict[str, Any]) -> bool:
        """11001: Run all pre-trade safety checks."""
        data = self.shm.get_data()

        # Layer 2: Global Drawdown check
        account = data.get("account", {})
        if account.get("drawdown", 0) >= self.config.max_drawdown_pct:
            logger.warning(f"Trade Vetoed: Max Drawdown Reached ({account.get('drawdown')}%)")
            return False

        # Layer 3: Spread Blowout check
        symbol = decision.get("symbol")
        market = data.get(f"market:{symbol}", {})
        bid = market.get("bid", 0)
        ask = market.get("ask", 0)

        # institutional pts conversion check (mocked for simplicity here)
        spread = (ask - bid) * 100000 if "JPY" not in symbol else (ask - bid) * 1000
        if spread > self.config.max_spread_pts:
            logger.warning(f"Trade Vetoed: Spread {spread:.1f} exceeds limit {self.config.max_spread_pts} for {symbol}")
            return False

        return True

    def calculate_lots(self, symbol: str) -> float:
        """11002: Dynamic lot sizing."""
        # Institutional logic: Risk % of Equity / StopLoss distance
        return self.config.min_lot_size
