from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.API.schemas.hybrid_response import HybridSearchResultSchema, HybridSearchResponseSchema

def map_hybrid_to_schema(hybrid: HybridSearchResult) -> HybridSearchResultSchema:
    ret = hybrid.retrieval_result
    return HybridSearchResultSchema(
        id=ret.doc_id,  
        title=ret.title,
        url=ret.url,
        source=ret.source,
        published_date=ret.date,
        snippet=ret.snippet or (ret.content[:200] + "..." if len(ret.content) > 200 else ret.content),
        authors=ret.authors,
        rrf_score=hybrid.rrf_score,
        sparse_score=hybrid.sparse_score,
        dense_score=hybrid.dense_score,
        sparse_rank=hybrid.sparse_rank,
        dense_rank=hybrid.dense_rank,
        source_type=hybrid.source_type,
        cross_encoder_score=hybrid.cross_encoder_score,
        relevance_score = hybrid.relevance_score,
        recency_factor = hybrid.recency_factor,
        personalization_similarity = hybrid.personalization_similarity,
        final_score=hybrid.final_score
    )

def map_hybrid_list_to_response(query: str, hybrids: List[HybridSearchResult]) -> HybridSearchResponseSchema:
    return HybridSearchResponseSchema(
        query=query,
        results=[map_hybrid_to_schema(h) for h in hybrids]
    )