from src.DI.web_search_container import WebSearchContainer
from src.DI.orchestration_container import OrchestrationContainer
from src.DI.ranking_container import RankingContainer
from src.DI.disperse_search_container import SearchContainer      
from src.DI.embeddings_container import EmbeddingsContainer 
from src.DI.chunking_container import ChunkingContainer

_search_container = SearchContainer()
_embeddings_container = EmbeddingsContainer()
_ranking_container = RankingContainer()
_orchestration_container = OrchestrationContainer()
_web_container = WebSearchContainer()
_persistence_container = ChunkingContainer()  # Contenedor de persistencia de chunks

# Inyectar las dependencias en el contenedor de búsqueda web 
_web_container.override_providers(
    chunking_service=_persistence_container.chunking_service
)

# Inyectar las dependencias en el contenedor de persistencia de chunks
_persistence_container.override_providers(
    vector_indexer=_embeddings_container.vector_indexer,
    index_service=_search_container.index_service
)
    
# Inyectar las dependencias en el contenedor de ranking
_ranking_container.override_providers(
    sparse_service=_search_container.retrieval_service,
    dense_searcher=_embeddings_container.vector_searcher,
)

# Inyectar las dependencias en el contenedor de orquestación
_orchestration_container.override_providers(
    fusion_service=_ranking_container.fusion_service ,        
    web_search=_web_container.web_search,
    chunk_persistence=_persistence_container.chunk_persistence,
    insufficiency_detector=_web_container.insufficiency_detector
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

def get_web_extended_hybrid():
    """Retorna el servicio de búsqueda híbrida extendida (fusión de dispersa, densa y web)"""
    return _orchestration_container.web_extended_hybrid()

def get_web_search_for_test():
    """Retorna una instancia de WebSearch para pruebas."""
    return _web_container.web_search()

def get_rag_service():
    # retriever = get_hybrid_service()
    # # Usamos el generador de Groq con el modelo que recomendamos
    # generator = GroqGenerator(model_id="llama-3.3-70b-versatile")
    # return RAGService(retriever, generator)     
    pass

