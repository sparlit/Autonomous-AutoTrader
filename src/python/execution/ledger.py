import aiosqlite
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_Ledger")

class TradeLedger:
    def __init__(self, db_path: str = "audit_records.db"):
        """
        Initialize a TradeLedger instance with a given database path.
        
        Parameters:
        	db_path (str): Path to the SQLite database file. Defaults to "audit_records.db".
        """
        self.db_path = db_path
        self._cache = {"peak_equity": 0.0, "active_trades": {}}

    async def init_db(self):
        """
        Initialize the database schema and populate the cache with persisted state.
        
        Creates the `trades` and `account_stats` tables if they do not already exist,
        then loads the peak equity and active trades into the in-memory cache.
        """
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

        # Hydrate Cache
        self._cache["peak_equity"] = await self.get_peak_equity_db()
        active = await self.get_active_trades_db()
        for t in active: self._cache["active_trades"][t["ticket"]] = t

    def get_cached_peak_equity(self) -> float:
        """
        Retrieve the cached peak equity value.
        
        Returns:
        	float: The peak equity value stored in the in-memory cache.
        """
        return self._cache["peak_equity"]

    def get_cached_active_trades(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve all active trades from cache, optionally filtered by symbol.
        
        Parameters:
        	symbol (str, optional): If provided, returns only trades with this symbol.
        
        Returns:
        	list[dict]: A list of dicts representing active trades.
        """
        trades = list(self._cache["active_trades"].values())
        if symbol: return [t for t in trades if t["symbol"] == symbol]
        return trades

    async def update_peak_equity(self, equity: float):
        """
        Update the peak equity if the provided value exceeds the current peak.
        """
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
        """
        Fetch the peak equity value from persistent storage.
        
        Returns:
            float: The stored peak equity value, or 0.0 if no record is found.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("SELECT val FROM account_stats WHERE key = 'peak_equity'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0.0

    async def record_intent(self, symbol: str, action: str, lots: float, sl: float, tp: float) -> int:
        """
        Record a trade intent with pending status.
        
        Parameters:
            symbol (str): The trading symbol
            action (str): The trade action
            lots (float): The quantity of lots to trade
            sl (float): The stop loss price
            tp (float): The take profit price
        
        Returns:
            int: The internal trade ID of the recorded intent
        """
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "INSERT INTO trades (symbol, action, lots, sl, tp, status) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, action, lots, sl, tp, "PENDING")
            )
            await conn.commit()
            return cursor.lastrowid

    async def update_execution(self, internal_id: int, ticket: int, status: str = "OPEN"):
        """
        Update a trade's execution details and refresh the cached record.
        
        Parameters:
            internal_id (int): The internal trade ID to update.
            ticket (int): The execution ticket number to assign to the trade.
            status (str): The trade status. Defaults to "OPEN".
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET ticket = ?, status = ? WHERE id = ?",
                (ticket, status, internal_id)
            )
            await conn.commit()

            # Update Cache
            async with conn.execute("SELECT * FROM trades WHERE id = ?", (internal_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    cols = [d[0] for d in cursor.description]
                    self._cache["active_trades"][ticket] = dict(zip(cols, row))

    async def get_active_trades_db(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Fetch all open trades from the database, optionally filtered by symbol.
        
        Parameters:
        	symbol (str, optional): If provided, filter results to trades with this symbol.
        
        Returns:
        	List[Dict[str, Any]]: Open trades retrieved from the database.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            query = "SELECT * FROM trades WHERE status = 'OPEN'" + (" AND symbol = ?" if symbol else "")
            params = (symbol,) if symbol else ()
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def close_trade(self, ticket: int):
        """
        Mark a trade as closed.
        
        Parameters:
            ticket (int): The trade identifier.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "UPDATE trades SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP WHERE ticket = ?",
                (ticket,)
            )
            await conn.commit()
            self._cache["active_trades"].pop(ticket, None)
