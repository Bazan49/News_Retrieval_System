from typing import Any, Dict, List

from RetrievalModule.Application.lmir_retriever import LMIRScoreFunction
from RetrievalModule.Domain.retrieval_result import RetrievalResult
from RetrievalModule.Domain.retriever_repository import RetrieverRepository
from RetrievalModule.Domain.stats_repository import StatsRepository
from RetrievalModule.Infrastructure.elasticsearch_query_preprocesor import ElasticsearchQueryPreprocessor


class RetrievalAppService():
    def __init__(self, repository: RetrieverRepository, stats_repository: StatsRepository, scorer: LMIRScoreFunction, preprocessor: ElasticsearchQueryPreprocessor, top_candidates: int = 200):
        self.repository = repository
        self.stats_repo: stats_repository # type: ignore
        self.scorer = scorer
        self.preprocessor = preprocessor
        self.top_candidates = top_candidates
    
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
        query_tokens = self.preprocessor.preprocess(query)
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
        results = []
        for doc, score in scored[:k]:
            snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
            results.append(RetrievalResult(
                url=doc.url,
                title=doc.title,
                content=doc.content,
                score=score,
                source=doc.source,
                snippet=snippet
            ).to_dict())
        return results

    async def get_stats(self) -> dict:
        await self._ensure_stats_loaded()
        return self.scorer.get_statistics()