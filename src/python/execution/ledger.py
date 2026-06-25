import aiosqlite
import logging
import time
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    """16000: Atomic persistent trade database."""
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path
        self._peak_equity = 0.0

    async def clear_ledger(self):
        """
        16001: Wipe the persistent database for a clean start.
        Magic: 16001
        """
        logger.info(f"🧹 Clearing Trade Ledger database: {self.db_path}")
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
                logger.info("✅ Database file removed.")
            except Exception as e:
                logger.error(f"❌ Failed to remove database file: {e}")
        await self.init_db()

    async def init_db(self):
        """
        16002: Schema initialization.
        Magic: 16002
        """
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
                    status TEXT,
                    partial_tp_hit INTEGER DEFAULT 0,
                    is_managed INTEGER DEFAULT 1,
                    timestamp REAL
                )
            """)
            await db.commit()

    async def record_intent(self, symbol: str, action: str, lots: float, sl: int, tp: int) -> int:
        """
        16003: Store trade intent.
        Magic: 16003
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO trades (symbol, action, lots, sl_pts, tp_pts, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING", time.time())
            )
            await db.commit()
            return cursor.lastrowid

    async def confirm_trade(self, internal_id: int, ticket: int, entry: float, sl: float, tp: float):
        """
        16007: Confirm MT5 execution success.
        Magic: 16007
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE trades SET ticket = ?, entry_price = ?, sl_price = ?, tp_price = ?, status = 'OPEN' WHERE id = ?",
                (ticket, entry, sl, tp, internal_id)
            )
            await db.commit()

    async def update_trade_from_sync(self, ticket: int, symbol: str, action: str, lots: float, sl: float, tp: float):
        """
        16008: Upsert trade from MT5 SYNC pulse.
        Magic: 16008
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM trades WHERE ticket = ?", (ticket,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    await db.execute(
                        "UPDATE trades SET sl_price = ?, tp_price = ?, status = 'OPEN' WHERE ticket = ?",
                        (sl, tp, ticket)
                    )
                else:
                    await db.execute(
                        "INSERT INTO trades (symbol, action, lots, ticket, sl_price, tp_price, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (symbol, action, lots, ticket, sl, tp, "OPEN", time.time())
                    )
            await db.commit()

    async def set_partial_hit(self, ticket: int):
        """
        16009: Record partial TP fulfillment.
        Magic: 16009
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE trades SET partial_tp_hit = 1 WHERE ticket = ?", (ticket,))
            await db.commit()

    async def close_trade(self, ticket: int):
        """
        16010: Mark trade as closed.
        Magic: 16010
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE trades SET status = 'CLOSED' WHERE ticket = ?", (ticket,))
            await db.commit()

    async def close_all_active_trades(self):
        """
        16011: Mark all active trades as closed.
        Magic: 16011
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE trades SET status = 'CLOSED' WHERE status = 'OPEN'")
            await db.commit()

    async def get_active_trades_db(self, symbol: str) -> List[Dict[str, Any]]:
        """
        16004: Retrieve open tickets.
        Magic: 16004
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM trades WHERE symbol = ? AND status = 'OPEN'", (symbol,)) as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    async def get_all_active_trades(self) -> List[Dict[str, Any]]:
        """
        16016: Retrieve all open tickets.
        Magic: 16016
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM trades WHERE status = 'OPEN'") as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    async def update_peak_equity(self, equity: float):
        """
        16005: Peak tracking.
        Magic: 16005
        """
        if equity > self._peak_equity:
            self._peak_equity = equity

    def get_cached_peak_equity(self) -> float:
        """
        16006: Thread-safe peak retrieval.
        Magic: 16006
        """
        return self._peak_equity
