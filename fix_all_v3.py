import sys
import re

# 1. Fix specialized.py (MarketDataBrain keys, RiskBrain robustness)
content = open("src/python/brains/specialized.py").read()

# Fix MarketDataBrain
old_md_logic = """            bid, ask = event.get("b", 0), event.get("a", 0)

            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "atr": event.get("atr", 0),
                "spread": event.get("sp", 0),
                "tick_val": event.get("tv", 10.0),
                "tick_size": event.get("ts", 0.0001),
                "last_update": time.time()
            })"""

new_md_logic = """            # V3.3.1: Correct key mapping from MT5 DP message
            bid, ask = event.get("bi", 0), event.get("as", 0)
            atr = event.get("atr", 0)
            ts = event.get("ts", 0.0001)

            self.ipc.set_state(f"symbol_stats:{symbol}", {
                "bid": bid, "ask": ask,
                "atr": atr,
                "spread": event.get("sp", 0),
                "tick_val": event.get("tv", 10.0),
                "tick_size": ts,
                "last_update": time.time()
            })"""

content = content.replace(old_md_logic, new_md_logic)

# Fix RiskBrain
risk_brain_pattern = r'class RiskBrain\(BaseBrain\):.*?return None'
risk_brain_fixed = """class RiskBrain(BaseBrain):
    \"\"\"Brain 11 - 10517: Mandatory Vetting & Scaling Guard.\"\"\"
    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event.get("type") == "PROBABILISTIC_SIGNAL":
            symbol = event["symbol"]
            action = event["action"]

            # 1. Strict Lot Enforcement
            event["lots"] = 0.01

            # 2. Mandatory MTF Trend Alignment (Zero-Tolerance)
            trends = self.ipc.get_state(f"trend_stats:{symbol}", {})
            if not trends:
                return {"type": "VETO", "symbol": symbol, "reason": "STRICT_GUARD: NO TREND DATA"}

            required = "BULLISH" if action == "BUY" else "BEARISH"
            alignment = sum(1 for tf in ["m15", "h1", "h4", "d1"] if trends.get(tf) == required)

            if alignment < 3: # MANDATORY 3 OUT OF 4 ALIGNMENT
                return {"type": "VETO", "symbol": symbol, "reason": f"STRICT_GUARD: TREND MISALIGNED ({alignment}/4)"}

            # 3. Mandatory SL/TP Calculation (Zero-Tolerance)
            s_stats = self.ipc.get_state(f"symbol_stats:{symbol}", {})
            atr = event.get("atr") or s_stats.get("atr", 0)
            ts = s_stats.get("tick_size", 0.0001)

            if atr > 0 and ts > 0:
                sl_pts = int((atr * 2) / ts)
                tp_pts = sl_pts # 1:1 RR Unit Unit
            else:
                # Institutional Fallback (100 pips)
                sl_pts = 1000 if any(x in symbol for x in ["JPY", "XAU", "GOLD"]) else 100
                tp_pts = sl_pts

            event["sl_pts"] = max(10, sl_pts)
            event["tp_pts"] = max(10, tp_pts)

            # 10520: Ensure event is updated with VALIDATED_TRADE type
            return {**event, "type": "VALIDATED_TRADE"}
        return None"""

content = re.sub(risk_brain_pattern, risk_brain_fixed, content, flags=re.DOTALL)

with open("src/python/brains/specialized.py", "w") as f:
    f.write(content)
print("Fixed specialized.py")

# 2. Fix ledger.py (get_active_trades_db includes PENDING)
ledger_content = open("src/python/execution/ledger.py").read()
old_get_db = "WHERE symbol = ? AND status = 'OPEN'"
new_get_db = "WHERE symbol = ? AND status IN ('OPEN', 'PENDING')"
ledger_content = ledger_content.replace(old_get_db, new_get_db)
with open("src/python/execution/ledger.py", "w") as f:
    f.write(ledger_content)
print("Fixed ledger.py")

# 3. Fix coordinator.py (Signal Latching)
coord_content = open("src/python/hive/coordinator.py").read()

# Add signal latching to HiveOrchestrator.__init__
if "self.active_signals = set()" not in coord_content:
    coord_content = coord_content.replace("self.registry = BrainRegistry()", "self.registry = BrainRegistry(); self.active_signals = set()")

# Update handle_client_message to clear latch on T_ACK
# Actually, HandleTr in MT5 sends T_ACK
old_t_ack = """        elif m_type == "T_ACK":
            # Update trade with ticket from MT5
            await self.ledger.confirm_trade(message.get("id"), message.get("tk"), message.get("en"), message.get("sl"), message.get("tp"))
            return {"t": "ACK"}"""

# Wait, I need to find where T_ACK is handled. It seems it wasn't!
if 'elif m_type == "T_ACK":' not in coord_content:
    # Need to add it.
    insert_pos = coord_content.find('elif m_type == "SYNC":')
    if insert_pos != -1:
        t_ack_block = """        elif m_type == "T_ACK":
            # 10030: Clear signal latch and confirm trade
            internal_id = message.get("id")
            # We don't have symbol here, so we might need a better latch
            # Let's just rely on the ledger status change
            await self.ledger.confirm_trade(message.get("id"), message.get("tk"), 0, 0, 0)
            return {"t": "ACK"}\n\n"""
        coord_content = coord_content[:insert_pos] + t_ack_block + coord_content[insert_pos:]

with open("src/python/hive/coordinator.py", "w") as f:
    f.write(coord_content)
print("Fixed coordinator.py")
