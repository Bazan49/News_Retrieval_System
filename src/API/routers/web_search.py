from fastapi import APIRouter, Depends, Query
from src.API.dependencies import get_web_search_for_test
from src.API.schemas.hybrid_response import HybridSearchResponseSchema
from src.API.mappers.hybrid_search_mapper import map_hybrid_list_to_response

router = APIRouter(prefix="/web-search", tags=["web-search"])

@router.get("/test", response_model=HybridSearchResponseSchema)
async def test_web_search(
    q: str = Query(..., description="Consulta de prueba"),
    max_results: int = Query(5, description="Número máximo de resultados web a obtener", ge=1, le=20),
    web_search = Depends(get_web_search_for_test)
):
    """
    Endpoint de prueba para el módulo de búsqueda web.
    Obtiene resultados de Google News RSS, los scrapea, chunkifica y los devuelve
    como HybridSearchResult (con source_type=WEB y rrf_score=0.0).
    No indexa los chunks en las bases de datos.
    """
    hybrids, _ = await web_search.fetch_web_results(q, max_results=max_results)
    return map_hybrid_list_to_response(q, hybrids)