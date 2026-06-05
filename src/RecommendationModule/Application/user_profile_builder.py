import time
import numpy as np
from typing import Optional, Dict, Tuple
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore
from src.FeedbackModule.domain.interfaces.feedback_repository import FeedbackRepository
from src.RecommendationModule.Domain.interfaces.search_history_repository import SearchHistoryRepository
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder

class UserProfileBuilder:
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        search_history_repo: SearchHistoryRepository,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,   # Interfaz para recuperar embeddings de documentos por ID
        like_weight: float = 1.0,
        dislike_weight: float = -1.0,
        max_queries: int = 20,
        profile_cache_ttl: int = 300   # tiempo de vida en segundos (5 minutos)
    ):
        self.feedback_repo = feedback_repo
        self.search_history_repo = search_history_repo
        self.embedder = embedder
        self.vector_store = vector_store
        self.like_weight = like_weight
        self.dislike_weight = dislike_weight
        self.max_queries = max_queries
        self.profile_cache_ttl = profile_cache_ttl
        self._profile_cache: Dict[str, Tuple[np.ndarray, float]] = {}   # user_id -> (profile, timestamp)

    async def _get_doc_embedding(self, doc_id: str, text: str) -> np.ndarray:
        """Devuelve el embedding del documento como vector 1D"""
        # Intentar recuperar desde el almacén vectorial
        emb = await self.vector_store.get_embedding_by_id(doc_id)
        if emb is not None:
            return emb.flatten()

        # Si no está, calcularlo con el embedder (improbable)
        emb = await self.embedder.encode_single(text)
        return emb.flatten()

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
                emb = await self._get_doc_embedding(fb.chunk_id, fb.chunk_content)
                vectors.append(emb.flatten())          # asegurar 1D
                weights.append(self.like_weight if fb.rating else self.dislike_weight)

        if include_queries:
            queries = await self.search_history_repo.get_recent_queries(user_id, limit=self.max_queries)
            for q in queries:
                emb = await self.embedder.encode_single(q)
                vectors.append(emb.flatten())          # asegurar 1D
                weights.append(query_weight)

        if not vectors:
            return None

        total_weight = sum(weights)
        if total_weight == 0:
            return None

        # Inicializar perfil con la dimensión correcta (todas las formas son (dim,))
        dim = vectors[0].shape[0]
        profile = np.zeros(dim)

        for vec, w in zip(vectors, weights):
            profile += w * vec
        profile /= total_weight

        # Guardar en caché
        self._profile_cache[user_id] = (profile, time.time())
        return profile