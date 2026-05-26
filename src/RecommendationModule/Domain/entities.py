from dataclasses import dataclass, field
from typing import List, Optional
from src.Common.RetrievalResult.retrieval_result import RetrievalResult

@dataclass
class UserProfile:
    user_id: str
    embedding: Optional[List[float]] = None          # vector promedio (likes + consultas)
    last_updated: Optional[str] = None

@dataclass
class RecommendationRequest:
    user_id: str
    max_results: int = 10
    include_likes: bool = True
    include_queries: bool = True
    query_weight: float = 0.3   # peso de las consultas frente a likes (1 - query_weight para likes)

@dataclass
class RecommendationResult:
    user_id: str
    recommended_docs: List[RetrievalResult]
    scores: List[float]          # similitud coseno