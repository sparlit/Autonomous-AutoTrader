import re
from typing import Dict, Any, List, Optional

class AssetNormalizationLayer:
    """
    11001: Institutional Asset Normalization.
    Handles broker-specific suffixes (e.g., EURUSD.pro, BTCUSD.m).
    Maps symbols to asset classes (Forex, Crypto, Metal, Stock).
    """
    def __init__(self):
        self.asset_map = {
            "XAU": "METAL", "XAG": "METAL", "XPT": "METAL",
            "BTC": "CRYPTO", "ETH": "CRYPTO", "SOL": "CRYPTO",
            "USOil": "COMMODITY", "UKOil": "COMMODITY"
        }

    def normalize(self, raw_symbol: str) -> str:
        """Strip broker suffixes. Logic: 11002"""
        # Strip common suffixes like .pro, .m, .x, _i
        clean = re.sub(r'(\.pro|\.m|\.x|_i|\.ecn)$', '', raw_symbol, flags=re.IGNORECASE)
        return clean.upper()

    def get_asset_class(self, symbol: str) -> str:
        """Identify asset class for risk weighting. Logic: 11003"""
        clean = self.normalize(symbol)

        # Check prefix mapping
        for prefix, a_class in self.asset_map.items():
            if clean.startswith(prefix): return a_class

        # Default heuristics
        if len(clean) == 6 and clean.isalpha(): return "FOREX"
        if len(clean) >= 3 and any(c.isdigit() for c in clean): return "CRYPTO"

        return "STOCK"

    def calculate_lot_step(self, symbol: str) -> float:
        """11005: Deterministic lot step based on asset class."""
        a_class = self.get_asset_class(symbol)
        if a_class == "CRYPTO": return 0.01
        if a_class == "FOREX": return 0.01
        return 0.1
