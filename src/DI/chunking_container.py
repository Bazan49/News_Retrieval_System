from dependency_injector import containers, providers
from src.Common.Chunking.Application.persistence_service import ChunkPersistenceService
from src.DI.Config.settings import Settings
from src.Common.Chunking.Infrastructure.newspaper_chunker import NewspaperChunker
from src.Common.Chunking.Application.chunking_service import ChunkingService

class ChunkingContainer(containers.DeclarativeContainer):
    
    settings = providers.Singleton(Settings)

    chunker = providers.Factory(
        NewspaperChunker,
        max_tokens=settings.provided.chunker_max_tokens,
        overlap_percent=settings.provided.overlap_percent,
        model_name=settings.provided.embedding_model
    )

    chunking_service = providers.Factory(
        ChunkingService,
        chunker=chunker
    )

    vector_indexer = providers.Dependency()
    index_service = providers.Dependency()

    chunk_persistence = providers.Factory(
            ChunkPersistenceService,
        vector_indexer=vector_indexer,
        index_service=index_service
    )