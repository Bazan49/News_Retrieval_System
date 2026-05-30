from typing import List, Optional, Tuple
import numpy as np
from src.RankingModule.Domain.Interfaces.scoring_strategy import ScoringStrategy
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.RecommendationModule.Application.user_profile_builder import UserProfileBuilder

class PersonalizationScoringStrategy(ScoringStrategy):
    """
    Estrategia que calcula la similitud coseno entre el perfil del usuario y cada documento,
    y guarda el valor en `result.personalization_similarity`.
    Necesita el `user_id` en el constructor; la instancia es específica para un usuario.
    """
    def __init__(
        self,
        profile_builder: UserProfileBuilder,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,
    ):
        self.profile_builder = profile_builder
        self.embedder = embedder
        self.vector_store = vector_store
        self._profile = None   # se cargará bajo demanda

    async def _load_profile(self, user_id:str) -> bool:
        """Carga el perfil del usuario"""
        if self._profile is None:
            profile = await self.profile_builder.build_embedding_profile(
                user_id=user_id,
                include_likes=True,
                include_queries=True,
                query_weight=0.3
            )
            if profile is None:
                return False
            self._profile = profile.flatten() if profile.ndim > 1 else profile
        return True

    async def apply(self, results: List[HybridSearchResult], user_id: Optional[str] = None):
        if not results or not user_id or not await self._load_profile(user_id):
            for r in results:
                r.personalization_similarity = 0.0
            return

        for res in results:
            doc_emb = await self.profile_builder._get_doc_embedding(res.doc_id, res.content)
            norm_product = np.linalg.norm(self._profile) * np.linalg.norm(doc_emb)
            sim = np.dot(self._profile, doc_emb) / norm_product if norm_product != 0 else 0.0
            res.personalization_similarity = sim