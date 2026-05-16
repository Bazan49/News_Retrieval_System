from abc import ABC, abstractmethod
from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class RankingStrategy(ABC):
    @abstractmethod
    def rerank(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        """
        Aplica una estrategia de re-ranking sobre una lista de resultados ya fusionados
        (p.ej., ajusta puntuaciones por frescura, autoridad, cross-encoder, etc.)
        y devuelve la lista reordenada.
        """
        pass