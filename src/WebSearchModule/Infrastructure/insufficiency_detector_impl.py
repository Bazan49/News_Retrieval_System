from typing import Any, Dict, List, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from src.DI.Config.settings import Settings

class SimpleInsufficientResultsDetector(InsufficientResultsDetector):
    def __init__(
        self, 
        min_results: int = 3,
        min_score_threshold: float = -50.0,
        empty_results_insufficient: bool = True,
        good_rrf_threshold: float = None,        
        min_content_length: int = None,          
        settings: Settings = None
    ):
        self.min_results = min_results
        self.min_score_threshold = min_score_threshold
        self.empty_results_insufficient = empty_results_insufficient
        if settings is None:
            settings = Settings()
        self.good_rrf_threshold = good_rrf_threshold if good_rrf_threshold is not None else getattr(settings, 'good_rrf_threshold', 0.018)
        self.min_content_length = min_content_length if min_content_length is not None else getattr(settings, 'min_content_length', 100)

    async def is_insufficient(
        self, 
        query: str, 
        retrieved_results: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> bool:
        score = await self.get_insufficiency_score(query, retrieved_results)
        return score > threshold

    async def get_insufficiency_score(
        self,
        query: str,
        retrieved_results: List[Dict[str, Any]]
    ) -> float:
        if not retrieved_results:
            return 1.0 if self.empty_results_insufficient else 0.0
        
        num_results = len(retrieved_results)
        if num_results < self.min_results:
            quantity_score = (self.min_results - num_results) / self.min_results
        else:
            quantity_score = 0.0
        
        scores = [r.get("score", 0.0) for r in retrieved_results if "score" in r]
        quality_score = 0.0
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score < self.min_score_threshold:
                difference = self.min_score_threshold - avg_score
                quality_score = min(1.0, difference / 100.0)
        
        insufficiency = (0.6 * quantity_score) + (0.4 * quality_score)
        return min(1.0, max(0.0, insufficiency))

    # Métodos adicionales para calidad de resultados
    def is_good_result(self, result: HybridSearchResult, best_rrf: float) -> bool:
        if result.rrf_score < self.good_rrf_threshold:
            return False
        if not result.content or len(result.content.strip()) < self.min_content_length:
            return False
        if not result.title or not result.title.strip():
            return False
        return True

    def filter_good_results(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        if not results:
            return []
        best = max(r.rrf_score for r in results)
        return [r for r in results if self.is_good_result(r, best)]

    def is_local_insufficient(self, good_local_count: int, k: int, extra: int = 5) -> Tuple[bool, int]:
        if good_local_count >= k:
            return False, 0
        needed = k - good_local_count
        needed = max(1, min(k, needed)) + extra
        return True, needed