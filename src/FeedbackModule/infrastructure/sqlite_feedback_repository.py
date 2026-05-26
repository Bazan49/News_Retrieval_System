import aiosqlite
from datetime import datetime
from typing import List, Optional
from src.FeedbackModule.domain.entities import Feedback

class SQLiteFeedbackRepository:
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path

    async def _init_db(self):
        
        async with aiosqlite.connect(self.db_path) as db:
            # Tabla principal
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    chunk_content TEXT,
                    rating INTEGER NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            # Índices
            await db.execute("CREATE INDEX IF NOT EXISTS idx_query ON feedback(query)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_user ON feedback(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_rating ON feedback(rating)")
            await db.commit()

    async def save(self, feedback: Feedback) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO feedback (query, chunk_id, chunk_content, rating, user_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (feedback.query, feedback.chunk_id, feedback.chunk_content,
                 1 if feedback.rating else 0,
                 feedback.user_id,
                 feedback.timestamp.isoformat())
            )
            await db.commit()

    async def get_positive_by_similar_query(self, query_text: str, limit: int = 20) -> List[Feedback]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                WHERE rating = 1 AND query LIKE ?
                LIMIT ?
            """, (f"%{query_text}%", limit))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]

    async def get_negative_by_similar_query(self, query_text: str, limit: int = 20) -> List[Feedback]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                WHERE rating = 0 AND query LIKE ?
                LIMIT ?
            """, (f"%{query_text}%", limit))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]
        
    async def get_all_positive(self, limit: int = 500) -> List[Feedback]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                WHERE rating = 1
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]

    async def get_all_negative(self, limit: int = 500) -> List[Feedback]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                WHERE rating = 0
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]

    async def get_all(self, limit: int = 1000) -> List[Feedback]:
        """Obtiene todos los feedbacks (sin filtrar por rating)."""
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]
    
    async def get_by_user_id(self, user_id: str, limit: int = 500) -> List[Feedback]:
        """Obtiene feedbacks de un usuario específico (likes y dislikes)."""
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT query, chunk_id, chunk_content, rating, user_id, timestamp
                FROM feedback
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit))
            rows = await cursor.fetchall()
            return [
                Feedback(
                    query=r[0], chunk_id=r[1], chunk_content=r[2],
                    rating=bool(r[3]), user_id=r[4],
                    timestamp=datetime.fromisoformat(r[5])
                ) for r in rows
            ]