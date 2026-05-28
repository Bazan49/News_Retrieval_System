from datetime import datetime, timedelta, timezone
from jose import jwt
from src.DI.Config.settings import Settings
from src.AuthModule.Domain.entities import User
from src.AuthModule.Domain.interfaces.user_repository import UserRepository

settings = Settings()

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # Verifica el hash recibido con el almacenado (comparación simple de strings)
    def verify_password_hash(self, received_hash: str, stored_hash: str) -> bool:
        return received_hash == stored_hash

    async def authenticate_user(self, username: str, password_hash: str) -> User | None:
        user = await self.user_repo.get_by_username(username)
        if not user or not self.verify_password_hash(password_hash, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)