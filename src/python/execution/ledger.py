import aiosqlite
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
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
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS account_stats (
                    key TEXT PRIMARY KEY,
                    val REAL
                )
            """)
            await conn.commit()

    async def update_peak_equity(self, equity: float):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT INTO account_stats (key, val) VALUES ('peak_equity', ?) "
                "ON CONFLICT(key) DO UPDATE SET val = MAX(val, excluded.val)",
                (equity,)
            )
            await conn.commit()

    async def get_peak_equity(self) -> float:
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("SELECT val FROM account_stats WHERE key = 'peak_equity'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0.0

    async def record_intent(self, symbol: str, action: str, lots: float, sl: float, tp: float) -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING")
            )
            await conn.commit()
            return cursor.lastrowid

    async def update_execution(self, internal_id: int, ticket: int, status: str = "OPEN"):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET ticket = ?, status = ? WHERE id = ?",
                (ticket, status, internal_id)
            )
            await conn.commit()

    async def get_active_trades(self, symbol: str = None) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM trades WHERE status = 'OPEN'" + (" AND symbol = ?" if symbol else ""),
                (symbol,) if symbol else ()
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def close_trade(self, ticket: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP WHERE ticket = ?",
                (ticket,)
            )
            await conn.commit()
