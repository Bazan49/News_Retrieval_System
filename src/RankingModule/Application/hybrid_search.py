import asyncio
from typing import List, Optional
from src.RankingModule.Domain.Interfaces import fusion_strategy
from src.RankingModule.Domain.Interfaces.ranking_strategy import RankingStrategy
from src.RetrievalModule.Application.retrieval_service import RetrievalAppService
from src.EmbeddingsModule.Application.vector_searcher_usecase import VectorSearcher
from src.RankingModule.Domain.Interfaces.fusion_strategy import FusionStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class FusionService:
    """
    Servicio de aplicación que orquesta la obtención de resultados de búsqueda
    y aplica la estrategia de fusión.
    """
    def __init__(
        self,
        sparse_service: RetrievalAppService,
        dense_searcher: VectorSearcher,
        fusion_strategy: FusionStrategy,
    ):
        self.sparse_service = sparse_service
        self.dense_searcher = dense_searcher
        self.fusion_strategy = fusion_strategy

    async def hybrid_search(
        self,
        query: str,
        k: int = 200,
        user_id: Optional[str] = None,
    ) -> List[HybridSearchResult]:
        # Ejecutar ambas búsquedas en paralelo
        sparse_task = self.sparse_service.retrieve(query, k=k)
        dense_task = self.dense_searcher.search(query, k=k)
        sparse_results, dense_results = await asyncio.gather(sparse_task, dense_task)

        # Fusionar usando la estrategia inyectada
        fused = await self.fusion_strategy.merge(sparse_results, dense_results)

        return fused