import asyncio
from typing import Optional, List
from src.RankingModule.Application.ranking_service import RankingService
from src.RankingModule.Domain.Interfaces.ranking_strategy import RankingStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.WebSearchModule.Application.use_cases.web_search_use_case import WebSearch
from src.Common.Chunking.Application.persistence_service import ChunkPersistenceService
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from src.RankingModule.Application.hybrid_search import FusionService  

import logging
logger = logging.getLogger("RAGModule.HybridRetrievalService") 

class RetrieverService:
    def __init__(
        self,
        fusion_service: FusionService, 
        ranking_service: RankingService,
        re_ranking_strategy: RankingStrategy,      
        web_search: WebSearch,
        chunk_persistence: ChunkPersistenceService,
        insufficiency_detector: InsufficientResultsDetector,
        activate_reranking: bool = True, 
    ):
        self.fusion_service = fusion_service
        self.ranking_service = ranking_service
        self.re_ranking_strategy = re_ranking_strategy
        self.web_search = web_search
        self.chunk_persistence = chunk_persistence
        self.insufficiency_detector = insufficiency_detector
        self.activate_reranking = activate_reranking
         
    async def retrieve(self, query: str, k: int , user_id: Optional[str] = None) -> List[HybridSearchResult]:

        logger.info("Iniciando recuperación para query='%s', user=%s, k=%d", query, user_id, k)

        # Búsqueda local
        local_results = await self.fusion_service.hybrid_search(query, k=k, user_id=user_id)

        # Verificar calidad de resultados locales
        good_local = self.insufficiency_detector.filter_good_results(local_results)
        logger.info("Resultados locales calificados (filtro de calidad) | count=%d", len(good_local))

        # Determinar si los resultados locales son insuficientes
        is_insufficient, web_needed = self.insufficiency_detector.is_local_insufficient(len(good_local), k)
        logger.info("Evaluación de suficiencia local | insuficiente=%s, resultados_web_necesarios=%d", 
                    is_insufficient, web_needed)

        # Si no es insuficiente, trabajar con los mejores resultados locales
        if not is_insufficient:
            results = good_local[:k]
        else:
            # Búsqueda web
            web_hybrids, web_chunks = await self.web_search.fetch_web_results(query, max_results=web_needed)
            # Guardar chunks web en segundo plano
            logger.info("Indexación de chunks web programada en segundo plano | count=%d", len(web_chunks))
            if web_chunks:
                asyncio.create_task(self._safe_store_chunks(web_chunks))
            results = self._merge_unique(good_local, web_hybrids)[:k]

        # Re‑ranking  
        if self.activate_reranking and len(results) > 0:
            results = await self.re_ranking_strategy.rerank(results, query=query)

        # Aplicar posicionamiento 
        results = await self.ranking_service.compute(results, user_id=user_id)

        return results

    async def _safe_store_chunks(self, chunks):
        try:
            await self.chunk_persistence.store_chunks(chunks)
            logger.info("Chunks web persistidos correctamente | count=%d", len(chunks))
        except Exception as e:
            logger.error("Error al indexar chunks web | error=%s", str(e), exc_info=True)

    def _merge_unique(self, local, web):
        """Combina resultados locales y web, 
        eliminando duplicados por URL, dando prioridad a los web."""
        seen = set()
        merged = []
        for item in web:
            if item.doc_id not in seen:
                seen.add(item.doc_id)
                merged.append(item)
        for item in local:
            if item.doc_id not in seen:
                seen.add(item.doc_id)
                merged.append(item)
        return merged