# src/Orchestration/fallback_helpers.py
from typing import Any, Dict, List, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

def to_dict_list(results: List[HybridSearchResult]) -> List[Dict[str, Any]]:
    """Convierte una lista de HybridSearchResult al formato que espera el detector."""
    dict_list = []
    for r in results:
        dict_list.append({
            "url": r.url,
            "title": r.title,
            "score": r.rrf_score,
            "rrf_score": r.rrf_score,
            "sparse_score": r.sparse_score,
            "dense_score": r.dense_score,
            "content": r.content
        })
    return dict_list

def is_good_result(result: HybridSearchResult, best_rrf: float, threshold: float = 0.018, min_content_len: int = 100) -> bool:
    if result.rrf_score < threshold:
        return False
    if not result.content or len(result.content.strip()) < min_content_len:
        return False
    if not result.title or not result.title.strip():
        return False
    return True

def filter_good_results(results: List[HybridSearchResult], threshold: float = 0.018, min_content_len: int = 100) -> List[HybridSearchResult]:
    if not results:
        return []
    best = max(r.rrf_score for r in results)
    return [r for r in results if is_good_result(r, best, threshold, min_content_len)]

def is_local_insufficient(good_local_count: int, k: int, extra: int = 5) -> Tuple[bool, int]:
    if good_local_count >= k:
        return False, 0
    needed = k - good_local_count
    needed = max(1, min(k, needed)) + extra
    return True, needed

def merge_unique(local: List[HybridSearchResult], web: List[HybridSearchResult]) -> List[HybridSearchResult]:
    seen = set()
    merged = []
    for item in web:
        if item.url not in seen:
            seen.add(item.url)
            merged.append(item)
    for item in local:
        if item.url not in seen:
            seen.add(item.url)
            merged.append(item)
    return merged