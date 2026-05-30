from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class ScoringStrategy(ABC):
    @abstractmethod
    async def apply(self, results: List[HybridSearchResult], user_id: Optional[str] = None):
        """
        Aplica la estrategia a los resultados, modificando sus campos de puntuación
        (por ejemplo, personalization_similarity, recency_factor, etc.).
        """
        pass