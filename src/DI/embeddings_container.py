from dependency_injector import containers, providers
from EmbbedingsModule.Domain.UseCases.vector_indexer_usecase import VectorIndexer
from EmbbedingsModule.Domain.UseCases.vector_searcher_usecase import VectorSearcher
from EmbbedingsModule.Domain.chunker import Chunker
from EmbbedingsModule.Domain.embedder import BaseEmbedder
from EmbbedingsModule.Domain.vector_store import BaseVectorStore
from EmbbedingsModule.Infrastructure.newspaper_chunker import NewspaperChunker
from EmbbedingsModule.Infrastructure.sentence_transformer_embedder import SentenceTransformerEmbedder
from EmbbedingsModule.Infrastructure.chroma_vector_store import ChromaVectorStore


class EmbeddingsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Infrastructure
    chunker = providers.Factory(
        NewspaperChunker,
        max_tokens=400,
        overlap=50
    )

    embedder = providers.Singleton(
        SentenceTransformerEmbedder,
        model_name="intfloat/multilingual-e5-large"
    )

    vector_store = providers.Singleton(
        ChromaVectorStore,
        collection_name="test_documents",
        persist_path="./chroma_db"
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