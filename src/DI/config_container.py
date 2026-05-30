from dependency_injector import containers, providers
from src.DI.Config.settings import Settings

class ConfigContainer(containers.DeclarativeContainer):
    """Contenedor central para la configuración de la aplicación."""
    settings = providers.Singleton(Settings)