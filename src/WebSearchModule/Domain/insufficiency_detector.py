from abc import ABC, abstractmethod
from typing import List, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class InsufficientResultsDetector(ABC):
    """Detecta si los resultados locales son insuficientes y activa búsqueda web."""

    @abstractmethod
    def filter_good_results(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        """Filtra los resultados que se consideran de suficiente calidad."""
        pass

    @abstractmethod
    def is_local_insufficient(self, good_local_count: int, k: int, extra: int = 5) -> Tuple[bool, int]:
        """
        Decide si la cantidad de resultados 'buenos' es insuficiente.
        Retorna (insufficient, web_needed).
        """
        pass