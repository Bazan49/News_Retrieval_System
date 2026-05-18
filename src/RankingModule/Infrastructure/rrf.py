from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from ..Domain.Interfaces.fusion_strategy import FusionStrategy
from ..Domain.Entities.hybrid_search_result import HybridSearchResult, ResultSource

class RRFFusionStrategy(FusionStrategy):
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    async def merge(
        self,
        sparse_results: List[RetrievalResult],
        dense_results: List[RetrievalResult]
    ) -> List[HybridSearchResult]:
        # Construir mapas de rango y score para cada documento
        sparse_map = {doc.url: (rank, doc.score) for rank, doc in enumerate(sparse_results, start=1)}
        dense_map = {doc.url: (rank, doc.score) for rank, doc in enumerate(dense_results, start=1)}

        # Calcular RRF scores
        rrf_scores = {}
        # Densos: primera ocurrencia
        for rank, doc in enumerate(dense_results, start=1):
            doc_id = doc.url
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 1 / (self.rrf_k + rank)
        # Dispersos: acumulando
        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc.url
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (self.rrf_k + rank)

        # Ordenar por puntaje RRF descendente
        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        top_ids = [doc_id for doc_id, _ in ranked]

        # Mapa de objetos (prioridad: disperso, luego denso)
        result_map = {doc.url: doc for doc in sparse_results}
        for doc in dense_results:
            if doc.url not in result_map:
                result_map[doc.url] = doc

        # Construir resultados híbridos con información completa
        results = []
        for doc_id in top_ids:
            ret = result_map[doc_id]
            s_rank, s_score = sparse_map.get(doc_id, (None, None))
            d_rank, d_score = dense_map.get(doc_id, (None, None))
            hybrid = HybridSearchResult(
                retrieval_result=ret,
                rrf_score=rrf_scores[doc_id],
                sparse_score=s_score,
                dense_score=d_score,
                sparse_rank=s_rank,
                dense_rank=d_rank,
                source_type=ResultSource.LOCAL
            )
            results.append(hybrid)
        return results