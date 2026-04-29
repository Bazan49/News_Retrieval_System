from dependency_injector import containers, providers
from src.DI.Config.settings import Settings
from src.EmbeddingsModule.Domain.UseCases.vector_indexer_usecase import VectorIndexer
from src.EmbeddingsModule.Domain.UseCases.vector_searcher_usecase import VectorSearcher
from src.EmbeddingsModule.Infrastructure.newspaper_chunker import NewspaperChunker
from src.EmbeddingsModule.Infrastructure.sentence_transformer_embedder import SentenceTransformerEmbedder
from src.EmbeddingsModule.Infrastructure.chroma_vector_store import ChromaVectorStore

class EmbeddingsContainer(containers.DeclarativeContainer):
    
    settings = providers.Singleton(Settings)

    # Infrastructure
    chunker = providers.Factory(
        NewspaperChunker,
        max_tokens=settings.provided.chunker_max_tokens,
        overlap_percent=settings.provided.overlap_percent,
        model_name=settings.provided.embedding_model
    )

    embedder = providers.Singleton(
        SentenceTransformerEmbedder,
        model_name=settings.provided.embedding_model,
        backend=settings.provided.embedding_backend
    )

    vector_store = providers.Singleton(
        ChromaVectorStore,
        collection_name=settings.provided.chroma_collection,
        host=settings.provided.chroma_host,
        port=settings.provided.chroma_port
    )
    
    # Use Cases
    vector_indexer = providers.Factory(
        VectorIndexer,
        chunker=chunker,
        embedder=embedder,
        vector_store=vector_store
    )

    vector_searcher = providers.Factory(
        VectorSearcher,
        embedder=embedder,
        vector_store=vector_store
    )