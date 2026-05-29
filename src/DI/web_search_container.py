from dependency_injector import containers, providers
from src.DI.Config.settings import Settings
from src.WebSearchModule.Application.use_cases.web_search_use_case import WebSearch
from src.WebSearchModule.Application.web_search_service import WebSearchService
from src.WebSearchModule.Infrastructure.rss.google_news_rss_fetcher import GoogleNewsRSSFetcher
from src.WebSearchModule.Infrastructure.insufficiency_detector_impl import SimpleInsufficientResultsDetector
from src.WebSearchModule.Infrastructure.web_search_document_processor import WebSearchDocumentProcessor

class WebSearchContainer(containers.DeclarativeContainer):
    """Container de inyección de dependencias para WebSearchModule."""
    
    settings = providers.Singleton(Settings)

    web_search_fetcher = providers.Singleton(
        GoogleNewsRSSFetcher,
        lang=settings.provided.google_news_lang,
        country=settings.provided.google_news_country
    )

    insufficiency_detector = providers.Singleton(
        SimpleInsufficientResultsDetector,
        min_results=3,
        min_score_threshold=-50.0,
        empty_results_insufficient=True,
        good_rrf_threshold=settings.provided.good_rrf_threshold,   
        min_content_length=settings.provided.min_content_length,
        settings=settings
    )

    # Aplicación
    chunking_service = providers.Dependency()

    web_search = providers.Factory(
        WebSearch,
        web_search_repo=web_search_fetcher,
        chunking_service=chunking_service    # Inyectado desde ChunkingContainer
    )
