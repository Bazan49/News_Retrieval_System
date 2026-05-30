from src.DI.config_container import ConfigContainer
from src.DI.feedback_container import FeedbackContainer
from src.DI.rag_container import RAGContainer
from src.DI.web_search_container import WebSearchContainer
from src.DI.orchestration_container import OrchestrationContainer
from src.DI.ranking_container import RankingContainer
from src.DI.disperse_search_container import SearchContainer      
from src.DI.embeddings_container import EmbeddingsContainer 
from src.DI.chunking_container import ChunkingContainer
from src.DI.recommendation_container import RecommendationContainer
from src.DI.auth_container import AuthContainer

_config_container = ConfigContainer()
_search_container = SearchContainer()
_embeddings_container = EmbeddingsContainer()
_ranking_container = RankingContainer()
_orchestration_container = OrchestrationContainer()
_web_container = WebSearchContainer()
_persistence_container = ChunkingContainer()  
_rag_container = RAGContainer()
_feedback_container = FeedbackContainer()
_recommendation_container = RecommendationContainer()
_auth_container = AuthContainer()

# Inyectar las dependencias en el contenedor de embeddings
_embeddings_container.override_providers(
    settings=_config_container.settings
)

# Inyectar las dependencias en el contenedor de búsqueda web
_web_container.override_providers(
    settings=_config_container.settings,
)

# Inyectar las dependencias en el contenedor de RAG
_rag_container.override_providers(
    settings=_config_container.settings,
)

# Inyectar las dependencias en el contenedor de búsqueda dispersa (LMIR + Elasticsearch)
_search_container.override_providers(
    settings=_config_container.settings,
)

# Inyectar las dependencias en el contenedor de búsqueda web 
_web_container.override_providers(
    settings=_config_container.settings,
    chunking_service=_persistence_container.chunking_service
)

# Inyectar las dependencias en el contenedor de persistencia de chunks
_persistence_container.override_providers(
    settings=_config_container.settings,
    vector_indexer=_embeddings_container.vector_indexer,
    index_service=_search_container.index_service
)

# Inyectar las dependencias en el contenedor de feedback
_feedback_container.override_providers(
    settings=_config_container.settings,
    embedder=_embeddings_container.embedder
)
    
# Inyectar las dependencias en el contenedor de ranking
_ranking_container.override_providers(
    settings=_config_container.settings,
    sparse_service=_search_container.retrieval_service,
    dense_searcher=_embeddings_container.vector_searcher,
    profile_builder=_recommendation_container.profile_builder,
    embedder=_embeddings_container.embedder,
    vector_store=_embeddings_container.vector_store,
)

# Inyectar las dependencias en el contenedor de recomendación
_recommendation_container.override_providers(
    settings=_config_container.settings,
    feedback_repo=_feedback_container.feedback_repository,
    embedder=_embeddings_container.embedder,
    vector_searcher=_embeddings_container.vector_searcher,
    vector_store=_embeddings_container.vector_store
)

# Inyectar las dependencias en el contenedor de orquestación
_orchestration_container.override_providers(
    fusion_service=_ranking_container.fusion_service,
    web_search=_web_container.web_search,
    chunk_persistence=_persistence_container.chunk_persistence,
    insufficiency_detector=_web_container.insufficiency_detector,
    ranking_service=_ranking_container.ranking_service,                 
    cross_encoder_strategy=_ranking_container.cross_encoder_strategy,   
    settings=_config_container.settings
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
    return _rag_container.rag_service()

def get_feedback_service():
    return _feedback_container.feedback_service()

def get_refinement_service():    
    return _feedback_container.refinement_service()

def get_recommender():
    return _recommendation_container.content_recommender()

def get_search_history_repo():
    return _recommendation_container.search_history_repo()

def get_auth_service():
    return _auth_container.auth_service()

def get_user_repository():
    return _auth_container.user_repository()