from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

def deduplicate(results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        """
        Dada una lista de resultados ya ordenada por relevancia (final_score descendente),
        conserva solo el primer chunk de cada documento (el mejor del documento).
        """
        seen_titles = set()
        unique = []
        for res in results:
            if res.title not in seen_titles:
                seen_titles.add(res.title)
                unique.append(res)
        return unique