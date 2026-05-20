from dataclasses import dataclass
from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
    
@dataclass
class RAGResult:
    query: str
    answer: str
    sources: List[HybridSearchResult]  