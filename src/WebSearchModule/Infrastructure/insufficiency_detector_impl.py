from typing import List, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector

class SimpleInsufficientResultsDetector(InsufficientResultsDetector):
    def __init__(
        self,
        max_dense_distance: float = 0.6,    
    ):
        self.max_dense_distance = max_dense_distance

    def is_good_result(self, result: HybridSearchResult) -> bool:

        if result.sparse_rank is not None and result.dense_rank is not None:
            # Híbrido: aceptado automáticamente
            return True
        elif result.dense_rank is not None:   
            if result.dense_score is not None and result.dense_score <= self.max_dense_distance:
                return True
            else:
                return False
        elif result.sparse_rank is not None:
            return True
        else:
            return False

    def filter_good_results(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        return [r for r in results if self.is_good_result(r)]

    def is_local_insufficient(self, good_local_count: int, k: int, extra: int = 5) -> Tuple[bool, int]:
        if good_local_count >= k:
            return False, 0
        needed = k - good_local_count
        needed = max(1, min(k, needed)) + extra
        return True, needed