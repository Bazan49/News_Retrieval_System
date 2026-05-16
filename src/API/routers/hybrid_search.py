from fastapi import APIRouter, Depends
from src.API.schemas.search_request import SearchQueryParams
from src.API.schemas.hybrid_response import HybridSearchResponseSchema
from src.API.mappers.hybrid_search_mapper import map_hybrid_list_to_response
from src.API.dependencies import get_hybrid_service

router = APIRouter(prefix="/hybrid", tags=["hybrid"])

@router.get("/", response_model=HybridSearchResponseSchema)
async def hybrid_search(
    params: SearchQueryParams = Depends(),
    service = Depends(get_hybrid_service)
):
    # service.hybrid_search devuelve List[HybridSearchResult]
    hybrid_results = await service.hybrid_search(params.q, k=params.k)
    return map_hybrid_list_to_response(params.q, hybrid_results)