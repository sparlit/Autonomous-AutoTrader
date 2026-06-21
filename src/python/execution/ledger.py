import aiosqlite
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    def __init__(self, db_path: str = "audit_records.db"):
        """Magic: 70001"""
        self.db_path = db_path
        self._cache = {"peak_equity": 0.0, "active_trades": {}}
        self.magic = 70001

    async def init_db(self):
        """Magic: 70002"""
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
                        open_price REAL,
                        is_managed INTEGER DEFAULT 0,
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

        self._cache["peak_equity"] = await self.get_peak_equity_db()
        active = await self.get_active_trades_db()
        for t in active: self._cache["active_trades"][t["ticket"]] = t

    def get_cached_peak_equity(self) -> float:
        """Magic: 70003"""
        return self._cache["peak_equity"]

    def get_cached_active_trades(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Magic: 70004"""
        trades = list(self._cache["active_trades"].values())
        if symbol: return [t for t in trades if t["symbol"] == symbol]
        return trades

    async def update_peak_equity(self, equity: float):
        """Magic: 70005"""
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
        """Magic: 70006"""
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("SELECT val FROM account_stats WHERE key = 'peak_equity'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0.0

    async def record_intent(self, symbol: str, action: str, lots: float, sl: float, tp: float) -> int:
        """Magic: 70007"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING")
            )
            await conn.commit()
            return cursor.lastrowid

    async def update_execution(self, internal_id: int, ticket: int, open_price: float = 0.0, status: str = "OPEN"):
        """Magic: 70008 - Corrected to accept open_price"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("BEGIN TRANSACTION")
            try:
                await conn.execute(
                    "UPDATE trades SET ticket = ?, status = ?, open_price = ? WHERE id = ?",
                    (ticket, status, open_price, internal_id)
                )
                if status == "OPEN":
                    async with conn.execute("SELECT * FROM trades WHERE id = ?", (internal_id,)) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            cols = [d[0] for d in cursor.description]
                            self._cache["active_trades"][ticket] = dict(zip(cols, row))
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                logger.error(f"Execution Update Failed: {e}")

    async def set_managed(self, ticket: int):
        """Magic: 70012"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("UPDATE trades SET is_managed = 1 WHERE ticket = ?", (ticket,))
            await conn.commit()
            if ticket in self._cache["active_trades"]:
                self._cache["active_trades"][ticket]["is_managed"] = 1

    async def adopt_trade(self, ticket: int, symbol: str):
        """Magic: 70009"""
        if ticket in self._cache["active_trades"]: return
        async with aiosqlite.connect(self.db_path) as conn:
            # We don't have the price here, but PositionManager will pivot safely
            await conn.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status, ticket) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (symbol, "ADOPTED", 0.0, 0, 0, "OPEN", ticket)
            )
            await conn.commit()
            active = await self.get_active_trades_db(symbol)
            for t in active: self._cache["active_trades"][t["ticket"]] = t

    async def get_active_trades_db(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Magic: 70010"""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            query = "SELECT * FROM trades WHERE status = 'OPEN'" + (" AND symbol = ?" if symbol else "")
            params = (symbol,) if symbol else ()
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def close_trade(self, ticket: int):
        """Magic: 70011"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP WHERE ticket = ?",
                (ticket,)
            )
            await conn.commit()
            self._cache["active_trades"].pop(ticket, None)
