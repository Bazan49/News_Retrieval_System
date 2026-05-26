import math
from datetime import datetime
from typing import List,Dict
from src.RankingModule.Domain.Interfaces.ranking_strategy import RankingStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.FeedbackModule.infrastructure.sqlite_feedback_repository import SQLiteFeedbackRepository
from src.FeedbackModule.application.refinement_service import RefinementService
from src.Common.Similarity.similarity_service import SimilarityService

class FeedbackRankingStrategy(RankingStrategy):
    def __init__(
        self,
        feedback_repo: SQLiteFeedbackRepository,
        refinement_service: RefinementService,
        similarity_service: SimilarityService,
        boost_factor: float = 0.3,        # +30% por like
        penalty_factor: float = 0.5,      # -50% por dislike
        recency_weight: float=0.5,        # peso de la frescura
        recency_decay_days: int = 30,     # días para que la frescura decaiga a la mitad
        similarity_threshold: float = 0.6,
        current_date: datetime = None
    ):
        self.feedback_repo = feedback_repo
        self.similarity_service = similarity_service
        self.boost_factor = boost_factor
        self.penalty_factor = penalty_factor
        self.recency_weight = recency_weight
        self.recency_decay_days = recency_decay_days
        self.similarity_threshold = similarity_threshold
        self.current_date = current_date or datetime.now()

    async def rerank(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        if not results:
            return results

        # 1. Obtener feedbacks similares a la consulta
        raise NotImplementedError("Se necesita la query original.")

    async def rerank_with_query(self, query: str, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        if not results:
            return results

        # 1. Obtener todos los feedbacks positivos y negativos (sin filtro textual)
        pos_feedbacks = await self.feedback_repo.get_all_positive(limit=500)
        neg_feedbacks = await self.feedback_repo.get_all_negative(limit=500)

        # 2. Calcular similitud semántica entre la consulta actual y cada feedback
        boost_map: Dict[str, float] = {}
        penalty_map: Dict[str, float] = {}

        # Procesar feedbacks positivos
        for fb in pos_feedbacks:
            sim = self.similarity_service.calculate_similarity(query, fb.query)
            if sim >= self.similarity_threshold:
                chunk_id = fb.chunk_id
                boost_map[chunk_id] = boost_map.get(chunk_id, 0) + self.boost_factor

        # Procesar feedbacks negativos
        for fb in neg_feedbacks:
            sim = self.similarity_service.calculate_similarity(query, fb.query)
            if sim >= self.similarity_threshold:
                chunk_id = fb.chunk_id
                penalty_map[chunk_id] = penalty_map.get(chunk_id, 0) + self.penalty_factor

        # 3. Aplicar ajustes a cada resultado
        for res in results:
            score = res.rrf_score
            chunk_id = res.retrieval_result.doc_id

            # Ajuste por feedback
            if chunk_id in boost_map:
                score *= (1 + boost_map[chunk_id])
            if chunk_id in penalty_map:
                score *= (1 - penalty_map[chunk_id])
                if score < 0:
                    score = 0.0

            # Ajuste por frescura (siempre se aplica, tenga o no feedback)
            pub_date = res.date
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    days_ago = (self.current_date - pub_date).days
                    if days_ago >= 0:
                        recency_boost = 1 + self.recency_weight * math.exp(-days_ago / self.recency_decay_days)
                        score *= recency_boost
                except Exception:
                    pass

            res.final_score = score

        # Ordenar por final_score (si no existe, usar rrf_score)
        results.sort(key=lambda x: x.final_score if x.final_score is not None else x.rrf_score, reverse=True)
        return results