from typing import List
from src.RetrievalModule.Application.lmir_retriever import LMIRScoreFunction
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
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
        
    async def retrieve(self, query: str, k: int = 10) -> List[RetrievalResult]:
        await self._ensure_stats_loaded()
        query_tokens = await self.preprocessor.preprocess(query)
        if not query_tokens:
            return []

        # Obtener chunks candidatos (cada uno es un DocumentData)
        candidates = await self.repository.get_candidate_documents(query_tokens, self.top_candidates)
        if not candidates:
            return []

        # Calcular puntuación LMIR para cada chunk
        scored = []
        for chunk in candidates:
            log_prob = self.scorer.compute_log_p_query_given_doc(query_tokens, chunk.chunk_id)  # Nota: usa chunk_id
            score = log_prob if log_prob != float('-inf') else -1e9
            scored.append((chunk, score))

        # Ordenar y tomar top k
        scored.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored[:k]

        # Normalizar scores (opcional)
        max_score = top_chunks[0][1] if top_chunks else 0
        min_score = top_chunks[-1][1] if top_chunks else 0
        score_range = max_score - min_score if max_score != min_score else 1

        results = []
        for chunk, score in top_chunks:
            normalized_score = 100 * (score - min_score) / score_range if score_range > 0 else 0
            # El snippet puede ser el contenido truncado o el contenido completo
            snippet = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            results.append(RetrievalResult(
                doc_id=chunk.chunk_id,        # ID único del chunk
                url=chunk.url,                # Documento padre
                title=chunk.title,
                content=chunk.content,        # Contenido completo del chunk
                score=normalized_score,
                source=chunk.source,
                snippet=snippet,
                authors=chunk.authors,
                date=chunk.date if chunk.date else None
            ))
        return results

    async def get_stats(self) -> dict:
        await self._ensure_stats_loaded()
        return self.scorer.get_statistics()