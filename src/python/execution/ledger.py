import aiosqlite
import logging
import time
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    """16000: Atomic persistent trade database (V3.3.0-ASCENDANT)."""
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path
        self._peak_equity = 0.0

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    action TEXT,
                    lots REAL,
                    sl_pts INTEGER,
                    tp_pts INTEGER,
                    ticket INTEGER DEFAULT 0,
                    entry_price REAL DEFAULT 0,
                    sl_price REAL DEFAULT 0,
                    tp_price REAL DEFAULT 0,
                    profit REAL DEFAULT 0,
                    status TEXT,
                    evidence TEXT,
                    timestamp REAL
                )
            """)
            await db.commit()

    async def record_intent(self, symbol: str, action: str, lots: float, sl: int, tp: int, evidence: str = "[]") -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO trades (symbol, action, lots, sl_pts, tp_pts, status, evidence, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING", evidence, time.time())
            )
            await db.commit()
            return cursor.lastrowid

    async def confirm_trade(self, internal_id: int, ticket: int, entry: float, sl: float, tp: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE trades SET ticket = ?, entry_price = ?, sl_price = ?, tp_price = ?, status = 'OPEN' WHERE id = ?",
                (ticket, entry, sl, tp, internal_id)
            )
            await db.commit()

    async def update_trade_from_sync(self, ticket: int, symbol: str, action: str, lots: float, sl: float, tp: float):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM trades WHERE ticket = ?", (ticket,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    await db.execute("UPDATE trades SET sl_price = ?, tp_price = ?, status = 'OPEN' WHERE ticket = ?", (sl, tp, ticket))
                else:
                    await db.execute(
                        "INSERT INTO trades (symbol, action, lots, ticket, sl_price, tp_price, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (symbol, action, lots, ticket, sl, tp, "OPEN", time.time())
                    )
            await db.commit()

    async def close_trade(self, ticket: int, profit: float = 0.0):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE trades SET status = 'CLOSED', profit = ? WHERE ticket = ?", (profit, ticket))
            await db.commit()

    async def get_active_trades_db(self, symbol: str) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM trades WHERE symbol = ? AND status = 'OPEN'", (symbol,)) as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    async def get_all_active_trades(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM trades WHERE status = 'OPEN'") as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    async def prune_trades(self, active_tickets: List[int]):
        async with aiosqlite.connect(self.db_path) as db:
            if not active_tickets:
                await db.execute("UPDATE trades SET status = 'CLOSED' WHERE status = 'OPEN'")
            else:
                sql_marks = ", ".join(["?"] * len(active_tickets))
                await db.execute(f"UPDATE trades SET status = 'CLOSED' WHERE status = 'OPEN' AND ticket NOT IN ({sql_marks})", active_tickets)
            await db.commit()
