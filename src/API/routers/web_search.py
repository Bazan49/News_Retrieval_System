from fastapi import APIRouter, Depends
from typing import List
from src.API.mappers.search_mapper import map_to_search_result_list
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult
from src.API.schemas.search_response import SearchResponseSchema
from src.API.dependencies import get_sparse_service, get_hybrid_service, get_dense_service, get_web_search_service
from src.API.schemas.search_request import SearchQueryParams

router = APIRouter(prefix="/search_web", tags=["search_web"])

@router.get("/sparse_web", response_model=SearchResponseSchema)
async def sparse_search(
    params: SearchQueryParams = Depends(),
    service = Depends(get_web_search_service),
    results= Depends(get_sparse_service)
):
    domain_results: List[RetrievalResult] = await results.retrieve(params.q, k=params.k)
    result = await service.search_with_fallback(
                    query=params.q,
                    local_results=domain_results,
                    web_results_limit=5,
                    insufficiency_threshold=0.5,
                    store_web_results=True
                )
    result = map_to_search_result_list(domain_results)
    return SearchResponseSchema(query=params.q, results=result)

