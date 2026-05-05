from fastapi import APIRouter, Depends
from src.RAG_Module.Application.rag_service import RAGService
from src.API.schemas.search_response import RAGResponseSchema
from src.API.mappers.rag_mapper import map_to_rag_response
from src.API.schemas.search_request import SearchQueryParams
from ..dependencies import get_rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.get("/", response_model=RAGResponseSchema)
async def rag_query(
    params: SearchQueryParams = Depends(),
    rag_service: RAGService = Depends(get_rag_service)
):
    result = await rag_service.answer(params.q, k=params.k)
    return map_to_rag_response(result)