import aiosqlite
import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    """16001: Atomic persistent trade database."""
    def __init__(self, db_path: str = "audit_records.db"):
        self.db_path = db_path
        self._peak_equity = 0.0

    async def init_db(self):
        """16002: Schema initialization."""
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
                    status TEXT,
                    timestamp REAL
                )
            """)
            await db.commit()

    async def record_intent(self, symbol: str, action: str, lots: REAL, sl: int, tp: int) -> int:
        """16003: Store trade intent before MT5 execution."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO trades (symbol, action, lots, sl_pts, tp_pts, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING", time.time())
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_trades_db(self, symbol: str) -> List[Dict[str, Any]]:
        """16004: Retrieve open tickets for reconciliation."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM trades WHERE symbol = ? AND status = 'OPEN'", (symbol,)) as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    async def update_peak_equity(self, equity: float):
        """16005: Atomic peak tracking for drawdown validation."""
        if equity > self._peak_equity:
            self._peak_equity = equity

    def get_cached_peak_equity(self) -> float:
        """16006: Thread-safe peak retrieval."""
        return self._peak_equity
