from abc import ABC, abstractmethod
from typing import List
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class FusionStrategy(ABC):
    
    @abstractmethod
    async def merge(
        self,
        sparse_results: List[RetrievalResult],
        dense_results: List[RetrievalResult]
    ) -> List[HybridSearchResult]:
        """
        Fusiona dos listas de resultados (dispersa y densa) y devuelve una lista
        de resultados híbridos con puntuaciones de fusión (ej. RRF).
        """
        pass