import math
import numpy as np
from datetime import datetime
from typing import List, Optional
from src.RankingModule.Domain.Interfaces.ranking_strategy import RankingStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.RecommendationModule.Application.user_profile_builder import UserProfileBuilder

class PersonalizedRankingStrategy(RankingStrategy):
    def __init__(
        self,
        profile_builder: UserProfileBuilder,
        embedder: BaseEmbedder,
        personalization_weight: float = 0.4,
        recency_weight: float = 0.2,
        recency_decay_days: int = 30,
        current_date: Optional[datetime] = None
    ):
        self.profile_builder = profile_builder
        self.embedder = embedder
        self.personalization_weight = personalization_weight
        self.recency_weight = recency_weight
        self.recency_decay_days = recency_decay_days
        self.current_date = current_date or datetime.now()
        self._doc_embedding_cache = {}

    async def _get_doc_embedding(self, doc_id: str, text: str) -> np.ndarray:
        """Obtiene el embedding de un documento, usando caché para evitar recálculos."""
        if doc_id in self._doc_embedding_cache:
            return self._doc_embedding_cache[doc_id]
        # Truncar texto a 1000 caracteres para eficiencia
        truncated = text[:1000] if len(text) > 1000 else text
        emb = await self.embedder.encode_single(truncated)
        self._doc_embedding_cache[doc_id] = emb
        return emb

    async def rerank(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        # Método genérico no utilizado, se prefiere rerank_with_user
        return results

    async def rerank_with_user(
        self,
        user_id: str,
        results: List[HybridSearchResult]
    ) -> List[HybridSearchResult]:
        if not user_id or not results:
            return results

        # Obtener perfil del usuario (vector promedio)
        profile = await self.profile_builder.build_embedding_profile(
            user_id=user_id,
            include_likes=True,
            include_queries=True,
            query_weight=0.3
        )
        if profile is None:
            return results

        # Ajustar cada resultado según similitud con el perfil
        for res in results:
            # Similitud con perfil
            doc_emb = await self._get_doc_embedding(res.doc_id, res.content)
            # Similitud coseno
            sim = np.dot(profile, doc_emb) / (np.linalg.norm(profile) * np.linalg.norm(doc_emb))
            # Score actual (final_score si existe, si no rrf_score)
            original_score = res.final_score if res.final_score is not None else res.rrf_score
            # Combinar
            personalized_score = original_score * (1 - self.personalization_weight) + sim * self.personalization_weight

            # Aplicar boost de frescura (si hay fecha)
            pub_date = res.date
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    days_ago = (self.current_date - pub_date).days
                    if days_ago >= 0:
                        recency_boost = 1 + self.recency_weight * math.exp(-days_ago / self.recency_decay_days)
                        personalized_score *= recency_boost
                except Exception:
                    pass

            res.final_score = personalized_score

        # Reordenar por final_score
        results.sort(key=lambda x: x.final_score if x.final_score is not None else x.rrf_score, reverse=True)
        return results