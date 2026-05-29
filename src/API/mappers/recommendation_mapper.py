from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from src.API.schemas.search_response import SearchResultItem
from src.API.schemas.recommendation_response import RecommendationResponse

def map_retrieval_to_search_item(ret: RetrievalResult) -> SearchResultItem:
    return SearchResultItem(
        id=ret.doc_id,
        title=ret.title,
        url=ret.url,
        source=ret.source,
        published_date=ret.date,
        score=ret.score,
        snippet=ret.snippet,
        authors=ret.authors or []
    )

def map_to_recommendation_response(user_id: str, docs: List[RetrievalResult]) -> RecommendationResponse:
    return RecommendationResponse(
        user_id=user_id,
        recommended_docs=[map_retrieval_to_search_item(d) for d in docs],
    )