from src.RAG_Module.Infrastructure.groq_generator import GroqGenerator
from src.RAG_Module.Application.rag_service import RAGService
from src.RetrievalModule.Application.hybrid_retrieval_service import HybridRetrievalAppService
from src.DI.continer import SearchContainer      
from src.DI.embeddings_container import EmbeddingsContainer 
from src.DI.web_search_container import WebSearchContainer 
from src.WebSearchModule.Application.web_search_service import WebSearchService
from dependency_injector import containers, providers


_search_container = SearchContainer()
_embeddings_container = EmbeddingsContainer()
_web_search_continer = WebSearchContainer()
_web_search_continer.config.from_value(_search_container.settings())
_web_search_continer.web_search_service.override(
    providers.Factory(
        WebSearchService,
        web_search_repo=_web_search_continer.web_search_fetcher,
        insufficiency_detector=_web_search_continer.insufficiency_detector,
        document_processor=_web_search_continer.document_processor,
        index_repository=_search_container.index_repository   # ← aquí inyectas el repositorio concreto
    )
)


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

def get_rag_service():
    retriever = get_hybrid_service()
    # Usamos el generador de Groq con el modelo que recomendamos
    generator = GroqGenerator(model_id="llama-3.3-70b-versatile")
    return RAGService(retriever, generator)             

def get_web_search_service():
    return _web_search_continer.web_search_service()