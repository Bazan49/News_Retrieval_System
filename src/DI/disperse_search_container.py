from dependency_injector import containers, providers
from src.IndexModule.Application.index_service import IndexService
from src.IndexModule.Domain.document_processor import DefaultDocumentProcessor
from src.IndexModule.Infrastructure.ElasticSearch.elasticsearch_index_repository import ElasticsearchIndexRepository
from src.IndexModule.Infrastructure.ElasticSearch.elasticsearch_client import ElasticsearchClient
from src.DI.Config.settings import Settings
from src.RetrievalModule.Application.retrieval_service import RetrievalAppService
from src.RetrievalModule.Application.lmir_retriever import LMIRScoreFunction
from src.RetrievalModule.Infrastructure.elasticsearch_retriever import ElasticsearchRetriever
from src.RetrievalModule.Infrastructure.elasticsearch_stats_repository import ElasticsearchStatsRepository
from src.RetrievalModule.Infrastructure.elasticsearch_query_preprocesor import ElasticsearchQueryPreprocessor

class SearchContainer(containers.DeclarativeContainer):
    
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