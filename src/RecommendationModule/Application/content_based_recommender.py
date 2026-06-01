import math
from datetime import datetime
from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from src.EmbeddingsModule.Application.vector_searcher_usecase import VectorSearcher
from src.RecommendationModule.Domain.entities import RecommendationRequest, RecommendationResult
from .user_profile_builder import UserProfileBuilder

class ContentRecommender:
    def __init__(
        self,
        profile_builder: UserProfileBuilder,
        vector_searcher: VectorSearcher,
        recency_weight: float = 0.2,
        recency_decay_days: int = 30
    ):
        self.profile_builder = profile_builder
        self.vector_searcher = vector_searcher
        self.recency_weight = recency_weight
        self.recency_decay_days = recency_decay_days

    async def recommend(self, request: RecommendationRequest) -> RecommendationResult:
        # Construir vector de perfil del usuario
        profile = await self.profile_builder.build_embedding_profile(
            user_id=request.user_id,
            include_likes=request.include_likes,
            include_queries=request.include_queries,
            query_weight=request.query_weight
        )
        if profile is None:
            return RecommendationResult(user_id=request.user_id, recommended_docs=[])

        # Obtener documentos similares (solicitar más para poder filtrar y reordenar)
        raw_results = await self.vector_searcher.search_by_vector(profile, k=request.max_results * 2)

        # Excluir documentos que el usuario ya ha valorado (likes o dislikes)
        user_feedbacks = await self.profile_builder.feedback_repo.get_by_user_id(request.user_id, limit=1000)
        excluded_ids = {fb.chunk_id for fb in user_feedbacks}   # chunk_id es la URL/ID del documento
        filtered_results = [doc for doc in raw_results if doc.doc_id not in excluded_ids]

        # Aplicar boost de frescura y ordenar
        current_date = datetime.now()
        final_results = []
        for doc in filtered_results:
            # Convertir distancia coseno a similitud (mayor = mejor)
            similarity = 1 - doc.score  # score original es distancia en ChromaDB
            if doc.date:
                try:
                    pub_date = datetime.fromisoformat(doc.date)
                    days_ago = (current_date - pub_date).days
                    if days_ago >= 0:
                        recency_boost = 1 + self.recency_weight * math.exp(-days_ago / self.recency_decay_days)
                        similarity *= recency_boost
                except Exception:
                    pass
            final_results.append((doc, similarity))

        # Ordenar por similitud boosteada descendente y truncar
        final_results.sort(key=lambda x: x[1], reverse=True)

        # Eliminar duplicados por URL
        final_results = self._deduplicate([doc for doc, _ in final_results])
        
        top_docs = final_results[:request.max_results]

        return RecommendationResult(
            user_id=request.user_id,
            recommended_docs=top_docs
        )
    
    def _deduplicate(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Dada una lista de resultados ya ordenada por relevancia (final_score descendente),
        conserva solo el primer chunk de cada documento (el mejor del documento).
        """
        seen_titles = set()
        unique = []
        for res in results:
            if res.title not in seen_titles:
                seen_titles.add(res.title)
                unique.append(res)
        return unique