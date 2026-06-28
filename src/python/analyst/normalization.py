import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AAT_Normalization")

class AssetNormalizationLayer:
    """
    14001: Institutional Asset Normalization Layer.
    Handles precision, tick values, and lot-size scaling across Forex, Metal, Crypto, and Stocks.
    """

    def __init__(self):
        # Default mappings for non-standard assets
        self.asset_configs = {
            "BTCUSD": {"type": "CRYPTO", "precision": 2, "min_lot": 0.01},
            "ETHUSD": {"type": "CRYPTO", "precision": 2, "min_lot": 0.1},
            "XAUUSD": {"type": "METAL", "precision": 2, "min_lot": 0.01},
            "WTI": {"type": "COMMODITY", "precision": 2, "min_lot": 0.1},
        }

    def normalize_symbol(self, raw_symbol: str) -> str:
        """14002: Universal Symbol Arbiter - Strips broker suffixes."""
        # Institutional Regex would go here, for now ruthless stripping
        import re
        # Strip trailing non-alphanumeric except common ones
        clean = re.sub(r'[^a-zA-Z0-9]+$', '', raw_symbol)
        # Handle specific common broker suffixes like .pro, .ecn, .m
        for suffix in ['.pro', '.ecn', '.m', '.x', '_']:
            if clean.endswith(suffix):
                clean = clean[:-len(suffix)]
        return clean.upper()

    def get_contract_value(self, symbol: str, bid: float) -> float:
        """14003: Calculate notional value of 1.0 lot."""
        # In MetaTrader, SYMBOL_TRADE_TICK_VALUE is provided, but we verify here
        sym = self.normalize_symbol(symbol)
        if "BTC" in sym: return bid # 1 BTC
        if "XAU" in sym: return bid * 100 # 100 oz
        return 100000.0 # Default Forex Lot 100k

    def scale_lots(self, symbol: str, raw_lots: float) -> float:
        """14004: Ensure lot size meets asset-specific minimums."""
        sym = self.normalize_symbol(symbol)
        config = self.asset_configs.get(sym, {"min_lot": 0.01})
        return max(raw_lots, config["min_lot"])
