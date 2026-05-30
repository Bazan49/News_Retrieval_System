from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.API.schemas.search_request import SearchQueryParams
from src.API.schemas.hybrid_response import HybridSearchResponseSchema
from src.API.mappers.hybrid_search_mapper import map_hybrid_list_to_response
from src.API.dependencies import get_hybrid_service, get_search_history_repo, get_web_extended_hybrid
from src.AuthModule.Application.dependencies import get_current_user_optional

router = APIRouter(prefix="/hybrid", tags=["hybrid"])

@router.get("/", response_model=HybridSearchResponseSchema)
async def hybrid_search_local(
    params: SearchQueryParams = Depends(),
    current_user: Optional[str] = Depends(get_current_user_optional),
    user_id_query: Optional[str] = Query(None, alias="user_id", description="ID de usuario (opcional, para anónimos)"),
    service = Depends(get_hybrid_service),
    history_repo = Depends(get_search_history_repo)
):
    """
    Búsqueda híbrida local (RRF + ranking, sin búsqueda web).
    - Si hay token de autenticación, se usa el usuario autenticado (current_user).
    - Si no, se usa el user_id pasado en la query string (si existe).
    - Si no hay ninguno, la búsqueda es anónima (no se guarda historial).
    """
    # Determinar el user_id: prioriza el token
    user_id = current_user or user_id_query
    # Guardar historial si hay user_id
    if user_id:
        await history_repo.save_query(user_id, params.q)

    hybrid_results = await service.hybrid_search(params.q, k=params.k, user_id=user_id)
    return map_hybrid_list_to_response(params.q, hybrid_results)

@router.get("/web", response_model=HybridSearchResponseSchema)
async def hybrid_search_web_extended(
    params: SearchQueryParams = Depends(),
    current_user: Optional[str] = Depends(get_current_user_optional),
    service = Depends(get_web_extended_hybrid),
    history_repo = Depends(get_search_history_repo)
):
    user_id = current_user or params.user_id
    if user_id:
        await history_repo.save_query(user_id, params.q)
    results = await service.retrieve(params.q, k=params.k, user_id=user_id)
    return map_hybrid_list_to_response(params.q, results)