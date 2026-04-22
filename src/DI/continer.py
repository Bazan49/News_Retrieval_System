from dependency_injector import containers, providers

from src.IndexModule.Application.index_service import IndexService
from src.IndexModule.Domain.document_processor import DefaultDocumentProcessor
from src.IndexModule.Infrastructure.ElasticSearch.elasticsearch_index_repository import ElasticsearchIndexRepository
from src.IndexModule.Infrastructure.ElasticSearch.elasticsearch_client import ElasticsearchClient
from src.IndexModule.Config.settings import Settings
from src.WebSearchModule.Application.web_search_service import WebSearchService
from src.WebSearchModule.Infrastructure.rss.google_news_rss_fetcher import GoogleNewsRSSFetcher
from src.WebSearchModule.Infrastructure.insufficiency_detector_impl import SimpleInsufficientResultsDetector
from src.WebSearchModule.Infrastructure.web_search_document_processor import WebSearchDocumentProcessor
from src.RetrievalModule.Application.retrieval_service import RetrievalAppService
from src.RetrievalModule.Application.lmir_retriever import LMIRScoreFunction
from src.RetrievalModule.Infrastructure.elasticsearch_retriever import ElasticsearchRetriever
from src.RetrievalModule.Infrastructure.elasticsearch_stats_repository import ElasticsearchStatsRepository
from src.RetrievalModule.Infrastructure.elasticsearch_query_preprocesor import ElasticsearchQueryPreprocessor

class SearchContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Singleton(Settings)

    es_client = providers.Singleton(
        ElasticsearchClient,
        hosts=settings.provided.elasticsearch_hosts,
        username=settings.provided.elasticsearch_username,
        password=settings.provided.elasticsearch_password,
        verify_certs=False,
    )

    document_processor = providers.Factory(DefaultDocumentProcessor)

    index_repository = providers.Factory(
        ElasticsearchIndexRepository,
        client=es_client.provided.async_client,
        index_name=settings.provided.index_name,
    )

    index_service = providers.Factory(
        IndexService,
        repository=index_repository,
        factory=document_processor,
    )

    # src.WebSearchModule dependencies
    web_search_fetcher = providers.Singleton(
        GoogleNewsRSSFetcher,
        lang="es-419",
        country="US"
    )

    insufficiency_detector = providers.Singleton(
        SimpleInsufficientResultsDetector,
        min_results=10,  # Aumentado para activar web search más fácilmente
        min_score_threshold=-50.0,
        empty_results_insufficient=True
    )

    web_search_document_processor = providers.Factory(WebSearchDocumentProcessor)

    web_search_service = providers.Factory(
        WebSearchService,
        web_search_repo=web_search_fetcher,
        insufficiency_detector=insufficiency_detector,
        document_processor=web_search_document_processor,
        index_repository=index_repository
    )

    # RetrievalModule dependencies
    retriever_repository = providers.Factory(
        ElasticsearchRetriever,
        client=es_client.provided.async_client,
        index_name=settings.provided.index_name,
    )

    stats_repository = providers.Factory(
        ElasticsearchStatsRepository,
        client=es_client.provided.async_client,
        index_name=settings.provided.index_name,
    )

    query_preprocessor = providers.Factory(
        ElasticsearchQueryPreprocessor,
        client=es_client.provided.async_client,
        index_name=settings.provided.index_name
    )

    lmir_scorer = providers.Singleton(LMIRScoreFunction, mu=100.0)

    retrieval_service = providers.Factory(
        RetrievalAppService,
        repository=retriever_repository,
        stats_repository=stats_repository,
        scorer=lmir_scorer,
        preprocessor=query_preprocessor,
        top_candidates=200
    )
