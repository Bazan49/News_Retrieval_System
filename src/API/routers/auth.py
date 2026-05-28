from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.AuthModule.Application.auth_service import AuthService
from src.AuthModule.Domain.entities import User
from src.API.dependencies import get_auth_service
from src.API.schemas.auth import UserRegisterRequest, TokenResponse, UserRegisterResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserRegisterResponse)
async def register(user_data: UserRegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    existing = await auth_service.user_repo.get_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(
        username=user_data.username,
        hashed_password=user_data.password_hash,
        email=user_data.email,
        full_name=user_data.full_name,
        disabled=False
    )
    await auth_service.user_repo.create(user)
    return UserRegisterResponse(msg="User created successfully")

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password hash",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token, token_type="bearer")