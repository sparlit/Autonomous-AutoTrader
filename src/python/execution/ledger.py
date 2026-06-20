import aiosqlite
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    def __init__(self, db_path: str = "audit_records.db"):
        """
        Initialize a TradeLedger instance with a given database path.
        """
        self.db_path = db_path
        self._cache = {"peak_equity": 0.0, "active_trades": {}}

    async def init_db(self):
        """
        Initialize the database schema and populate the cache with persisted state.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("BEGIN TRANSACTION")
            try:
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
            except Exception as e:
                await conn.rollback()
                logger.error(f"DB Init Failed: {e}")
                raise

        # Hydrate Cache
        self._cache["peak_equity"] = await self.get_peak_equity_db()
        active = await self.get_active_trades_db()
        for t in active: self._cache["active_trades"][t["ticket"]] = t

    def get_cached_peak_equity(self) -> float:
        return self._cache["peak_equity"]

    def get_cached_active_trades(self, symbol: str = None) -> List[Dict[str, Any]]:
        trades = list(self._cache["active_trades"].values())
        if symbol: return [t for t in trades if t["symbol"] == symbol]
        return trades

    async def update_peak_equity(self, equity: float):
        if equity > self._cache["peak_equity"]:
            self._cache["peak_equity"] = equity
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    "INSERT INTO account_stats (key, val) VALUES ('peak_equity', ?) "
                    "ON CONFLICT(key) DO UPDATE SET val = MAX(val, excluded.val)",
                    (equity,)
                )
                await conn.commit()

    async def get_peak_equity_db(self) -> float:
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
        """
        Atomic update of trade execution.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("BEGIN TRANSACTION")
            try:
                await conn.execute(
                    "UPDATE trades SET ticket = ?, status = ? WHERE id = ?",
                    (ticket, status, internal_id)
                )
                if status == "OPEN":
                    async with conn.execute("SELECT * FROM trades WHERE id = ?", (internal_id,)) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            cols = [d[0] for d in cursor.description]
                            trade_dict = dict(zip(cols, row))
                            self._cache["active_trades"][ticket] = trade_dict
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                logger.error(f"Execution Update Failed: {e}")

    async def adopt_trade(self, ticket: int, symbol: str):
        """
        Institutional Trade Adoption: Record an unknown trade found on MT5.
        """
        if ticket in self._cache["active_trades"]: return

        async with aiosqlite.connect(self.db_path) as conn:
            # Check if it already exists in DB
            async with conn.execute("SELECT * FROM trades WHERE ticket = ?", (ticket,)) as cursor:
                if await cursor.fetchone(): return

            # Adopt into DB and Cache
            await conn.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status, ticket) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (symbol, "UNKNOWN", 0.0, 0, 0, "OPEN", ticket)
            )
            await conn.commit()
            logger.info(f"ADOPTED orphan trade: {ticket} on {symbol}")
            # Refresh cache
            active = await self.get_active_trades_db(symbol)
            for t in active: self._cache["active_trades"][t["ticket"]] = t

    async def get_active_trades_db(self, symbol: str = None) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            query = "SELECT * FROM trades WHERE status = 'OPEN'" + (" AND symbol = ?" if symbol else "")
            params = (symbol,) if symbol else ()
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def close_trade(self, ticket: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP WHERE ticket = ?",
                (ticket,)
            )
            await conn.commit()
            self._cache["active_trades"].pop(ticket, None)
