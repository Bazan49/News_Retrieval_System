from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from src.DI.Config.settings import Settings
from src.API.dependencies import get_user_repository
from src.AuthModule.Infrastructure.sqlite_user_repository import SQLiteUserRepository

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not username:
            return None
        repo = SQLiteUserRepository(db_path=settings.users_db_path)
        user = await repo.get_by_username(username)
        if user and not user.disabled:
            return username
    except JWTError as e:
        print(f"Error JWT: {e}")
    except Exception as e:
        print(f"Otro error: {e}")
    return None

async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    return await get_current_user(token)