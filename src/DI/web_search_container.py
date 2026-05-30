from dependency_injector import containers, providers
from src.WebSearchModule.Application.use_cases.web_search_use_case import WebSearch
from src.WebSearchModule.Infrastructure.rss.google_news_rss_fetcher import GoogleNewsRSSFetcher
from src.WebSearchModule.Infrastructure.insufficiency_detector_impl import SimpleInsufficientResultsDetector

class WebSearchContainer(containers.DeclarativeContainer):
    """Container de inyección de dependencias para WebSearchModule."""
    
    settings = providers.Dependency() #ConfigContainer.settings

    web_search_fetcher = providers.Singleton(
        GoogleNewsRSSFetcher,
        lang=settings.provided.google_news_lang,
        country=settings.provided.google_news_country
    )

    insufficiency_detector = providers.Singleton(
        SimpleInsufficientResultsDetector,
        min_results=3,
        min_score_threshold=-50.0,
        empty_results_insufficient=True
    )

    # Aplicación
    chunking_service = providers.Dependency()

    web_search = providers.Factory(
        WebSearch,
        web_search_repo=web_search_fetcher,
        chunking_service=chunking_service    # Inyectado desde ChunkingContainer
    )
