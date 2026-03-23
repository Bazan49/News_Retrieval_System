from dependency_injector import containers, providers

from IndexModule.Application.index_service import IndexService
from IndexModule.Domain.document_processor import DefaultDocumentProcessor
from IndexModule.Infrastructure.ElasticSearch.elasticsearch_index_repository import ElasticsearchIndexRepository
from IndexModule.Infrastructure.ElasticSearch.elasticsearch_client import ElasticsearchClient
from IndexModule.Config.settings import Settings


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
