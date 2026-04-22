from dependency_injector import containers, providers
from src.EmbbedingsModule.Domain.UseCases.vector_indexer_usecase import VectorIndexer
from src.EmbbedingsModule.Domain.UseCases.vector_searcher_usecase import VectorSearcher
from src.EmbbedingsModule.Domain.chunker import Chunker
from src.EmbbedingsModule.Domain.embedder import BaseEmbedder
from src.EmbbedingsModule.Domain.vector_store import BaseVectorStore
from src.EmbbedingsModule.Infrastructure.newspaper_chunker import NewspaperChunker
from src.EmbbedingsModule.Infrastructure.sentence_transformer_embedder import SentenceTransformerEmbedder
from src.EmbbedingsModule.Infrastructure.chroma_vector_store import ChromaVectorStore


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
        model_name= "all-MiniLM-L6-v2" #intfloat/multilingual-e5-large",
        # backend="onnx"
    )

    vector_store = providers.Singleton(
        ChromaVectorStore,
        collection_name="news_embeddings",
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