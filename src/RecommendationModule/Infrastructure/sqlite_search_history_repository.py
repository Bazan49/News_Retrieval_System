import aiosqlite
from datetime import datetime
from typing import List
from src.RecommendationModule.Domain.interfaces.search_history_repository import SearchHistoryRepository

class SQLiteSearchHistoryRepository(SearchHistoryRepository):
    def __init__(self, db_path: str = "search_history.db"):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_user ON search_history(user_id)")

    async def save_query(self, user_id: str, query: str) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO search_history (user_id, query, timestamp) VALUES (?, ?, ?)",
                (user_id, query, datetime.now().isoformat())
            )
            await db.commit()

    async def get_recent_queries(self, user_id: str, limit: int = 20) -> List[str]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]