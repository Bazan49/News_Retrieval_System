from pydantic import BaseModel
from typing import Optional

# Request schemas
class UserRegisterRequest(BaseModel):
    username: str
    password_hash: str
    email: Optional[str] = None
    full_name: Optional[str] = None

# Si quieres usar un esquema para login (aunque OAuth2PasswordRequestForm ya funciona)
class UserLoginRequest(BaseModel):
    username: str
    password_hash: str

# Response schemas
class UserRegisterResponse(BaseModel):
    msg: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str