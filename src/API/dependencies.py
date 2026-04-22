from src.RetrievalModule.Application.hybrid_retrieval_service import HybridRetrievalAppService
from src.DI.continer import SearchContainer      
from src.DI.embeddings_container import EmbeddingsContainer 

_search_container = SearchContainer()
_embeddings_container = EmbeddingsContainer()

def get_sparse_service():
    """Retorna el servicio de búsqueda dispersa (LMIR + Elasticsearch)"""
    return _search_container.retrieval_service()

def get_hybrid_service():
    """Retorna el servicio de búsqueda híbrida (RRF)"""
    sparse = get_sparse_service()
    dense = get_dense_service()
    return HybridRetrievalAppService(sparse, dense, rrf_k=60)

def get_dense_service():
    """Retorna el servicio de búsqueda densa (embeddings + ChromaDB)"""
    return _embeddings_container.vector_searcher()