from abc import ABC, abstractmethod
from typing import List, Optional
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class RankingStrategy(ABC):
    @abstractmethod
    def rerank(self, results: List[HybridSearchResult], query: Optional[str]) -> List[HybridSearchResult]:
        """
        Aplica una estrategia de re-ranking sobre una lista de resultados ya fusionados
        (p.ej. cross-encoder, re-ranking basado en características, etc.)
        y devuelve la lista reordenada.
        """
        pass