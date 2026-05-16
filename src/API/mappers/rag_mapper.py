from src.RAG_Module.Domain.rag_result import RAGResult
from src.API.schemas.rag_response import RAGResponseSchema
from src.API.mappers.search_mapper import map_to_search_result_item

def map_to_rag_response(rag_result: RAGResult) -> RAGResponseSchema:
    """Convierte RAGResult (dominio) a RAGResponseSchema (API)."""
    sources = [map_to_search_result_item(doc) for doc in rag_result.sources]
    return RAGResponseSchema(
        query=rag_result.query,
        answer=rag_result.answer,
        sources=sources
    )