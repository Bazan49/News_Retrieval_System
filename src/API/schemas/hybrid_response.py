from pydantic import BaseModel
from typing import Optional, List
from src.RankingModule.Domain.Entities.hybrid_search_result import ResultSource

class HybridSearchResultSchema(BaseModel):
    # Campos del resultado base
    id: str                     
    title: str
    url: str
    source: str
    published_date: Optional[str] = None          
    snippet: str
    authors: Optional[List[str]] = None
    
    # Campos específicos del híbrido
    rrf_score: float
    sparse_score: Optional[float] = None
    dense_score: Optional[float] = None
    sparse_rank: Optional[int] = None
    dense_rank: Optional[int] = None
    source_type: ResultSource   # "local" o "web"
    cross_encoder_score: Optional[float] = None  # puntuación del cross-encoder
    relevance_score: Optional[float] = None
    recency_factor: Optional[float] = None
    personalization_similarity: Optional[float] = None
    final_score: Optional[float] = None  # puntuación final después de reranking

class HybridSearchResponseSchema(BaseModel):
    query: str
    results: List[HybridSearchResultSchema]