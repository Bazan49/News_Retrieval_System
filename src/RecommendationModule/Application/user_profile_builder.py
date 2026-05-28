import time
import numpy as np
from typing import List, Optional, Dict, Tuple
from src.FeedbackModule.infrastructure.sqlite_feedback_repository import SQLiteFeedbackRepository
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.RecommendationModule.Infrastructure.sqlite_search_history_repository import SQLiteSearchHistoryRepository

class UserProfileBuilder:
    def __init__(
        self,
        feedback_repo: SQLiteFeedbackRepository,
        search_history_repo: SQLiteSearchHistoryRepository,
        embedder: feedback_repo.em,
        like_weight: float = 1.0,
        dislike_weight: float = -0.5,
        max_queries: int = 20,
        profile_cache_ttl: int = 300   # tiempo de vida en segundos (5 minutos)
    ):
        self.feedback_repo = feedback_repo
        self.search_history_repo = search_history_repo
        self.embedder = embedder
        self.like_weight = like_weight
        self.dislike_weight = dislike_weight
        self.max_queries = max_queries
        self.profile_cache_ttl = profile_cache_ttl
        self._embedding_cache = {}
        self._profile_cache: Dict[str, Tuple[np.ndarray, float]] = {}   # user_id -> (profile, timestamp)

    async def _get_embedding(self, text: str) -> np.ndarray:
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        emb = await self.embedder.encode_single(text)
        self._embedding_cache[text] = emb
        return emb

    async def build_embedding_profile(
        self,
        user_id: str,
        include_likes: bool = True,
        include_queries: bool = True,
        query_weight: float = 0.3
    ) -> Optional[np.ndarray]:
        # Verificar caché de perfil
        if user_id in self._profile_cache:
            profile, timestamp = self._profile_cache[user_id]
            if time.time() - timestamp < self.profile_cache_ttl:
                return profile

        vectors = []
        weights = []

        if include_likes:
            user_feedbacks = await self.feedback_repo.get_by_user_id(user_id, limit=500)
            for fb in user_feedbacks:
                emb = await self._get_embedding(fb.chunk_content)
                weight = self.like_weight if fb.rating else self.dislike_weight
                vectors.append(emb)
                weights.append(weight)

        if include_queries:
            queries = await self.search_history_repo.get_recent_queries(user_id, limit=self.max_queries)
            for q in queries:
                emb = await self._get_embedding(q)
                vectors.append(emb)
                weights.append(query_weight)

        if not vectors:
            return None

        total_weight = sum(weights)
        if total_weight == 0:
            return None

        profile = np.zeros(vectors[0].shape)
        for vec, w in zip(vectors, weights):
            profile += w * vec
        profile /= total_weight

        # Guardar en caché
        self._profile_cache[user_id] = (profile, time.time())
        return profile