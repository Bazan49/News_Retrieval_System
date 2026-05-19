from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from src.API.schemas.search_response import SearchResultItem

def map_to_search_result_item(result: RetrievalResult) -> SearchResultItem:
    """Convierte un objeto de dominio a schema de API."""
    return SearchResultItem(
        id=result.doc_id,
        title=result.title,
        url=result.url,
        source=result.source,
        published_date=result.date,   
        score=result.score,
        snippet=result.snippet,
        authors=result.authors or []
    )

def map_to_search_result_list(results: List[RetrievalResult]) -> List[SearchResultItem]:
    return [map_to_search_result_item(r) for r in results]