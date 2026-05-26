import numpy as np
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
        personalization_weight: float = 0.4
    ):
        self.profile_builder = profile_builder
        self.embedder = embedder
        self.personalization_weight = personalization_weight
        self._doc_embedding_cache = {}   # cache: doc_id -> embedding vector

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
            # Obtener embedding del documento (desde caché o calculado)
            doc_emb = await self._get_doc_embedding(res.doc_id, res.content)
            # Similitud coseno
            sim = np.dot(profile, doc_emb) / (np.linalg.norm(profile) * np.linalg.norm(doc_emb))
            # Score actual (final_score si existe, si no rrf_score)
            original_score = res.final_score if res.final_score is not None else res.rrf_score
            # Combinar
            personalized_score = original_score * (1 - self.personalization_weight) + sim * self.personalization_weight
            res.final_score = personalized_score

        # Reordenar por final_score
        results.sort(key=lambda x: x.final_score if x.final_score is not None else x.rrf_score, reverse=True)
        return results