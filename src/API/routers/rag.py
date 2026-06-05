from typing import Optional
from fastapi import APIRouter, Depends
from src.API.schemas.rag_response import RAGResponseSchema
from src.API.schemas.search_request import SearchQueryParams
from src.API.dependencies import get_rag_orchestrator, get_search_history_repo
from src.API.mappers.rag_mapper import map_to_rag_response

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.get("/", response_model=RAGResponseSchema)
async def rag_query(
    params: SearchQueryParams = Depends(),
    orchestrator = Depends(get_rag_orchestrator),
    history_repo = Depends(get_search_history_repo)
):
    user_id = params.user_id
    if user_id:
        await history_repo.save_query(user_id, params.q)
    result = await orchestrator.search(params.q, k=params.k, user_id=params.user_id)
    return map_to_rag_response(result)