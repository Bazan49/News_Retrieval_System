from typing import Any, Dict, List

from src.RetrievalModule.Application.lmir_retriever import LMIRScoreFunction
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult
from src.RetrievalModule.Domain.retriever_repository import RetrieverRepository
from src.RetrievalModule.Domain.stats_repository import StatsRepository
from src.RetrievalModule.Domain.query_preprocessor import QueryPreprocessor


class RetrievalAppService():
    def __init__(self, repository: RetrieverRepository, stats_repository: StatsRepository, scorer: LMIRScoreFunction, preprocessor: QueryPreprocessor, top_candidates: int = 200):
        self.repository = repository
        self.stats_repo = stats_repository
        self.scorer = scorer
        self.preprocessor = preprocessor
        self.top_candidates = top_candidates
        self._stats_loaded = False
    
    async def _ensure_stats_loaded(self):
        """Carga las estadísticas en el scorer la primera vez."""
        if self._stats_loaded:
            return
        doc_term_freqs = await self.stats_repo.get_doc_term_freqs()
        doc_lengths = await self.stats_repo.get_doc_lengths()
        collection_freq = await self.stats_repo.get_collection_freq()
        self.scorer.load_statistics(doc_term_freqs, doc_lengths, collection_freq)
        self._stats_loaded = True
        
    async def retrieve(self, query: str, k: int = 10) -> List[Dict[str, Any]]: 
        await self._ensure_stats_loaded()
        query_tokens = await self.preprocessor.preprocess(query)
        if not query_tokens:
            return []

        # Obtener candidatos
        candidates = await self.repository.get_candidate_documents(query_tokens, self.top_candidates)
        if not candidates:
            return []

        # Calcular puntuaciones
        scored = []
        for doc in candidates:
            log_prob = self.scorer.compute_log_p_query_given_doc(query_tokens, doc.doc_id)
            score = log_prob if log_prob != float('-inf') else -1e9
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Normalizar scores para mejor legibilidad
        max_score = scored[0][1] if scored else 0
        min_score = scored[-1][1] if scored else 0
        score_range = max_score - min_score if max_score != min_score else 1
        
        results = []
        for doc, score in scored[:k]:
            # Normalizar a 0-100
            normalized_score = 100 * (score - min_score) / score_range if score_range > 0 else 0
            snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
            results.append(RetrievalResult(
                url=doc.url,
                title=doc.title,
                content=doc.content,
                score=normalized_score,  # Score normalizado
                source=doc.source,
                snippet=snippet
            ).to_dict())
        return results

    async def get_stats(self) -> dict:
        await self._ensure_stats_loaded()
        return self.scorer.get_statistics()