from fastapi import APIRouter, Depends
from src.RAGModule.Application.rag_service import RAGService
from src.API.schemas.rag_response import RAGResponseSchema
from src.API.schemas.search_request import SearchQueryParams
from src.API.dependencies import get_hybrid_service, get_rag_service
from src.API.mappers.rag_mapper import map_to_rag_response

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.get("/", response_model=RAGResponseSchema)
async def rag_query(
    params: SearchQueryParams = Depends(),
    retrieval_service = Depends(get_hybrid_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    # 1. Obtener resultados híbridos para la consulta
    hybrid_results = await retrieval_service.hybrid_search(params.q, k=params.k)
    # 2. Generar respuesta RAG
    result = await rag_service.answer(params.q, hybrid_results)
    # 3. Convertir a schema de respuesta
    return map_to_rag_response(result)