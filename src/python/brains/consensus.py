import pandas as pd
from src.python.analyst.price_action import SMCAnalyst
from src.python.analyst.indicators import IndicatorAnalyst
from src.python.analyst.volatility import VolatilityAnalyst
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

class ConsensusEngine:
    def __init__(self):
        """
        Initialize the consensus engine with analyst components and a thread pool for concurrent analysis.

        Sets up three specialized analysts:
        - SMCAnalyst: Detects market structure, order blocks, and candlestick triggers
        - IndicatorAnalyst: Calculates technical indicators (RSI, ATR, etc.)
        - VolatilityAnalyst: Analyzes volatility and volume spread analysis (VSA)

        Also initializes a ThreadPoolExecutor with 4 workers for parallel computation.
        """
        self.smc = SMCAnalyst()
        self.indicators = IndicatorAnalyst()
        self.volatility = VolatilityAnalyst()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)

    def _parse_history(self, raw_h: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        Convert raw candle history into normalized dictionary format.

        Parameters:
		raw_h (List[List[Any]]): Raw candle data where each inner list is [open, high, low, close, time, volume]

        Returns:
		List[Dict[str, Any]]: List of candles with keys o, h, l, c, t, v for open, high, low, close, time, and volume
        """
        return [{"o": x[0], "h": x[1], "l": x[2], "c": x[3], "t": x[4], "v": x[5]} for x in raw_h]

    def analyze_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market history and produce a trading decision with diagnostic scoring.

        Performs synchronous technical analysis of OHLCV data across multiple timeframes,
        computing momentum, market structure, volatility, and order block signals to derive
        a consolidated trading action (BUY, SELL, or WAIT) along with component scores and
        visualization commands.

        Parameters:
            data: Dictionary containing market history. Expected keys:
                - 'history': Candles for the primary timeframe
                - 'h4': Optional candles for the higher timeframe

        Returns:
            Dictionary with:
                - 'action': Trading decision (BUY, SELL, or WAIT)
                - 'score': Total composite score
                - 'details': Component scores (trend, momentum, structure, volatility)
                - 'vsa': Volume spread analysis results
                - 'atr': Average True Range value
                - 'sweep': Market structure sweep classification
                - 'trigger': Candlestick trigger signal
                - 'htf_trend': Higher timeframe trend direction
                - 'proximity_msg': HTF proximity rejection flag or False
                - 'draw': Drawing commands for visualization
        """
        hist_data = data.get("history", [])
        if hist_data and isinstance(hist_data[0], list): hist_data = self._parse_history(hist_data)
        if not hist_data: return {"action": "WAIT", "reason": "No history"}
        df = pd.DataFrame(hist_data)

        h4_raw = data.get("h4", [])
        if h4_raw and isinstance(h4_raw[0], list): h4_raw = self._parse_history(h4_raw)
        h4_df = pd.DataFrame(h4_raw)

        f_htf = self._thread_pool.submit(self.smc.detect_market_structure, h4_df) if not h4_df.empty else None
        f_inds = self._thread_pool.submit(self.indicators.calculate_all, df)
        f_vsa = self._thread_pool.submit(self.volatility.analyze_vsa, df)
        f_trig = self._thread_pool.submit(self.smc.detect_candlestick_trigger, df)

        inds = f_inds.result()
        atr = inds["atr"]
        structure = self.smc.detect_market_structure(df, atr=atr)
        htf_struct = f_htf.result() if f_htf else {"trend": "NEUTRAL", "swing_h": 0, "swing_l": 0}
        vsa = f_vsa.result()
        trigger = f_trig.result()

        curr_price = df['c'].iloc[-1]
        proximity_rejection = False
        if htf_struct["swing_h"] and curr_price >= htf_struct["swing_h"] - (atr * 0.5): proximity_rejection = "NEAR_HTF_RESISTANCE"
        if htf_struct["swing_l"] and curr_price <= htf_struct["swing_l"] + (atr * 0.5): proximity_rejection = "NEAR_HTF_SUPPORT"

        momentum = "NEUTRAL"
        if inds["rsi"] > 60: momentum = "BULLISH"
        elif inds["rsi"] < 40: momentum = "BEARISH"

        obs = self.smc.detect_order_blocks(df, atr=atr)
        near_ob = False; active_ob = None
        for ob in obs:
            if ob["type"] == "BULLISH" and curr_price <= ob["top"] + (atr * 0.1): near_ob = True; active_ob = ob
            elif ob["type"] == "BEARISH" and curr_price >= ob["bottom"] - (atr * 0.1): near_ob = True; active_ob = ob

        regime = self.volatility.get_regime(df)

        scores = {
            "trend": 1 if structure["trend"] == "BULLISH" else (-1 if structure["trend"] == "BEARISH" else 0),
            "momentum": 1 if momentum == "BULLISH" else (-1 if momentum == "BEARISH" else 0),
            "structure": 1 if near_ob and structure["trend"] == "BULLISH" else (-1 if near_ob and structure["trend"] == "BEARISH" else 0),
            "volatility": 1 if regime != "HIGH_VOLATILITY" else 0
        }

        if htf_struct["trend"] == "BULLISH" and structure["trend"] == "BULLISH": scores["trend"] += 1
        if htf_struct["trend"] == "BEARISH" and structure["trend"] == "BEARISH": scores["trend"] -= 1

        if vsa["effort"] == "HIGH" and vsa["result"] == "STRONG":
            if structure["trend"] == "BULLISH": scores["momentum"] += 1
            elif structure["trend"] == "BEARISH": scores["momentum"] -= 1

        if structure["sweep"] == "BULLISH_SWEEP": scores["structure"] += 2
        elif structure["sweep"] == "BEARISH_SWEEP": scores["structure"] -= 2

        trigger_confirmed = False
        if trigger:
            if "BULLISH" in trigger and (scores["trend"] + scores["structure"]) > 0: trigger_confirmed = True
            if "BEARISH" in trigger and (scores["trend"] + scores["structure"]) < 0: trigger_confirmed = True

        total_score = sum(scores.values())
        action = "WAIT"
        if trigger_confirmed and not proximity_rejection:
            if total_score >= 3: action = "BUY"
            elif total_score <= -3: action = "SELL"

        draw_commands = []
        if active_ob:
            draw_commands.append({
                "type": "RECTANGLE", "name": f"OB_{active_ob['type']}_{active_ob['index']}",
                "top": active_ob["top"], "bottom": active_ob["bottom"],
                "color": "0,255,0" if active_ob["type"] == "BULLISH" else "255,0,0"
            })

        return {
            "action": action, "score": total_score, "details": scores,
            "vsa": vsa, "atr": atr, "sweep": structure["sweep"], "trigger": trigger,
            "htf_trend": htf_struct["trend"], "proximity_msg": proximity_rejection,
            "draw": draw_commands
        }
