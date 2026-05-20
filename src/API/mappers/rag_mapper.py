from src.RAGModule.Domain.rag_result import RAGResult
from src.API.schemas.rag_response import RAGResponseSchema
from src.API.mappers.hybrid_search_mapper import map_hybrid_to_schema   

def map_to_rag_response(rag_result: RAGResult) -> RAGResponseSchema:
    """Convierte RAGResult (dominio) a RAGResponseSchema (API)."""
    sources = [map_hybrid_to_schema(hybrid) for hybrid in rag_result.sources]
    return RAGResponseSchema(
        query=rag_result.query,
        answer=rag_result.answer,
        sources=sources
    )