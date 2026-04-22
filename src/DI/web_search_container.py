from dependency_injector import containers, providers

from src.WebSearchModule.Application.web_search_service import WebSearchService
from src.WebSearchModule.Infrastructure.rss.google_news_rss_fetcher import GoogleNewsRSSFetcher
from src.WebSearchModule.Infrastructure.insufficiency_detector_impl import SimpleInsufficientResultsDetector
from src.WebSearchModule.Infrastructure.web_search_document_processor import WebSearchDocumentProcessor


class WebSearchContainer(containers.DeclarativeContainer):
    """Container de inyección de dependencias para WebSearchModule."""
    
    # Configuración
    config = providers.Configuration()

    # Infraestructura
    web_search_fetcher = providers.Singleton(
        GoogleNewsRSSFetcher,
        lang="es-419",  # Español latino
        country="US"
    )

    insufficiency_detector = providers.Singleton(
        SimpleInsufficientResultsDetector,
        min_results=3,
        min_score_threshold=-50.0,
        empty_results_insufficient=True
    )

    document_processor = providers.Factory(WebSearchDocumentProcessor)

    # Aplicación - requiere index_repository del otro container
    web_search_service = providers.Factory(
        WebSearchService,
        web_search_repo=web_search_fetcher,
        insufficiency_detector=insufficiency_detector,
        document_processor=document_processor,
        index_repository=providers.Dependency()  # Inyectado desde SearchContainer
    )
