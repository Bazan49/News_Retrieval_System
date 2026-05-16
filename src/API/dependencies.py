from src.DI.ranking_container import RankingContainer
from src.DI.disperse_search_container import SearchContainer      
from src.DI.embeddings_container import EmbeddingsContainer 

_search_container = SearchContainer()
_embeddings_container = EmbeddingsContainer()
_ranking_container = RankingContainer()

# Inyectar las dependencias en el contenedor de ranking
_ranking_container.override_providers(
    sparse_service=_search_container.retrieval_service,
    dense_searcher=_embeddings_container.vector_searcher,
)

def get_sparse_service():
    """Retorna el servicio de búsqueda dispersa (LMIR + Elasticsearch)"""
    return _search_container.retrieval_service()

def get_dense_service():
    """Retorna el servicio de búsqueda densa (embeddings + ChromaDB)"""
    return _embeddings_container.vector_searcher()

def get_hybrid_service():
    """Retorna el servicio de búsqueda híbrida (fusión de dispersa y densa)"""
    return _ranking_container.fusion_service()

def get_rag_service():
    # retriever = get_hybrid_service()
    # # Usamos el generador de Groq con el modelo que recomendamos
    # generator = GroqGenerator(model_id="llama-3.3-70b-versatile")
    # return RAGService(retriever, generator)     
    pass

