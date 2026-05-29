import aiosqlite
from typing import Optional
from src.AuthModule.Domain.entities import User
from src.AuthModule.Domain.interfaces.user_repository import UserRepository

class SQLiteUserRepository(UserRepository):
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    hashed_password TEXT NOT NULL,
                    email TEXT,
                    full_name TEXT,
                    disabled BOOLEAN DEFAULT 0
                )
            """)
            await db.commit()

    async def get_by_username(self, username: str) -> Optional[User]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT username, hashed_password, email, full_name, disabled FROM users WHERE username = ?",
                (username,)
            )
            row = await cursor.fetchone()
            if row:
                return User(
                    username=row[0],
                    hashed_password=row[1],
                    email=row[2],
                    full_name=row[3],
                    disabled=bool(row[4])
                )
            return None

    async def create(self, user: User) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO users (username, hashed_password, email, full_name, disabled) VALUES (?, ?, ?, ?, ?)",
                (user.username, user.hashed_password, user.email, user.full_name, user.disabled)
            )
            await db.commit()