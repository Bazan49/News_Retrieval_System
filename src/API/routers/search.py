from fastapi import APIRouter, Depends
from typing import List
from src.API.mappers.search_mapper import map_to_search_result_list
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult
from src.API.schemas.search_response import SearchResponseSchema
from src.API.dependencies import get_sparse_service, get_dense_service
from src.API.schemas.search_request import SearchQueryParams

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/sparse", response_model=SearchResponseSchema)
async def sparse_search(
    params: SearchQueryParams = Depends(),
    service = Depends(get_sparse_service)
):
    domain_results: List[RetrievalResult] = await service.retrieve(params.q, k=params.k)
    api_results = map_to_search_result_list(domain_results)
    return SearchResponseSchema(query=params.q, results=api_results)

@router.get("/dense", response_model=SearchResponseSchema)
async def dense_search(
    params: SearchQueryParams = Depends(),
    service = Depends(get_dense_service)
):
    domain_results: List[RetrievalResult] = await service.search(params.q, k=params.k)
    api_results = map_to_search_result_list(domain_results)
    return SearchResponseSchema(query=params.q, results=api_results)
    