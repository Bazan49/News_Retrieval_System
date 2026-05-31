from dependency_injector import containers, providers
from src.AuthModule.Infrastructure.sqlite_user_repository import SQLiteUserRepository
from src.AuthModule.Application.auth_service import AuthService

class AuthContainer(containers.DeclarativeContainer):
    settings = providers.Dependency()
    user_repository = providers.Singleton(SQLiteUserRepository, db_path=settings.provided.users_db_path)
    auth_service = providers.Factory(AuthService, user_repo=user_repository)