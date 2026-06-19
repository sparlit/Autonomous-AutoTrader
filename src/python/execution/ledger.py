import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    action TEXT,
                    lots REAL,
                    sl REAL,
                    tp REAL,
                    status TEXT,
                    ticket INTEGER DEFAULT 0,
                    open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    close_time TIMESTAMP
                )
            """)
            conn.commit()

    def record_intent(self, symbol: str, action: str, lots: float, sl: float, tp: float) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING")
            )
            conn.commit()
            return cursor.lastrowid

    def update_execution(self, internal_id: int, ticket: int, status: str = "OPEN"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE trades SET ticket = ?, status = ? WHERE id = ?",
                (ticket, status, internal_id)
            )
            conn.commit()

    def get_active_trades(self, symbol: str = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if symbol:
                cursor.execute("SELECT * FROM trades WHERE symbol = ? AND status = 'OPEN'", (symbol,))
            else:
                cursor.execute("SELECT * FROM trades WHERE status = 'OPEN'")
            return [dict(row) for row in cursor.fetchall()]

    def close_trade(self, ticket: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE trades SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP WHERE ticket = ?",
                (ticket,)
            )
            conn.commit()
