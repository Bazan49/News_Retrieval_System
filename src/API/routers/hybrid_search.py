from typing import Optional

from fastapi import APIRouter, Depends
from src.API.schemas.search_request import SearchQueryParams
from src.API.schemas.hybrid_response import HybridSearchResponseSchema
from src.API.mappers.hybrid_search_mapper import map_hybrid_list_to_response
from src.API.dependencies import get_hybrid_service, get_search_history_repo, get_web_extended_hybrid

router = APIRouter(prefix="/hybrid", tags=["hybrid"])

@router.get("/", response_model=HybridSearchResponseSchema)
async def hybrid_search_local(
    params: SearchQueryParams = Depends(),
    user_id: Optional[str] = None,
    service = Depends(get_hybrid_service),
    history_repo = Depends(get_search_history_repo)
):
    """Búsqueda híbrida local (RRF + ranking, sin búsqueda web)."""
    hybrid_results = await service.hybrid_search(params.q, k=params.k)
    if user_id:
        await history_repo.save_query(user_id, params.q)
    return map_hybrid_list_to_response(params.q, hybrid_results)

@router.get("/web", response_model=HybridSearchResponseSchema)
async def hybrid_search_web_extended(
    params: SearchQueryParams = Depends(),
    user_id: Optional[str] = None,
    service = Depends(get_web_extended_hybrid),
    history_repo = Depends(get_search_history_repo)
):
    """Búsqueda híbrida con fallback a web si los resultados locales son insuficientes."""
    if params.user_id:
        await history_repo.save_query(params.user_id, params.q)
    results = await service.search(params.q, k=params.k, user_id=params.user_id)
    return map_hybrid_list_to_response(params.q, results)