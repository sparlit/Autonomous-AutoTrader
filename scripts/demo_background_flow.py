import asyncio
import json
import time
from typing import Dict, Any

# Mocking parts of the system to show the "Process Flow"
class MockIPC:
    def __init__(self):
        self.state = {}
    def set_state(self, key, val):
        print(f"[BACKGROUND] IPC Update: {key} -> {json.dumps(val)}")
        self.state[key] = val
    def get_all_state(self):
        return self.state

async def simulate_dashboard_cycle():
    ipc = MockIPC()

    print("\n--- PHASE 1: Data Ingestion (MT5 Bridge) ---")
    # Coordinator receives a heartbeat or data push
    ipc.set_state("account_stats", {
        "equity": 10500.50,
        "drawdown": 1.25,
        "pos_count": 2,
        "spread": 1.5,
        "last_hb": time.time()
    })

    print("\n--- PHASE 2: Brain Swarm Processing ---")
    # Brains publish their findings to IPC keys
    ipc.set_state("trend_stats:EURUSD", {
        "m15": "BULLISH", "h1": "BULLISH", "h4": "BULLISH", "d1": "NEUTRAL"
    })

    print("\n--- PHASE 3: Position Enrichment (Orchestrator Loop) ---")
    # Orchestrator reads TradeLedger and enriches with tick data
    active_trades = [
        {
            "ticket": 987654, "symbol": "EURUSD", "action": "BUY", "lots": 0.01,
            "entry_price": 1.0840, "pl_currency": 12.50, "status": "OPEN",
            "sl_price": 1.0840, "reason": "MTF_ALIGNED_CONF_3"
        }
    ]
    ipc.set_state("active_trades", active_trades)

    print("\n--- PHASE 4: Web Server WebSocket Push ---")
    # web_server.py reads ALL_STATE and serializes to JSON for the browser
    all_state = ipc.get_all_state()
    json_payload = json.dumps(all_state)
    print(f"WEB_SERVER: Sending payload to React client ({len(json_payload)} bytes)")
    print(f"SAMPLE DATA: {json_payload[:150]}...")

if __name__ == "__main__":
    asyncio.run(simulate_dashboard_cycle())
