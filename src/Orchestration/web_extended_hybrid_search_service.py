import asyncio
from typing import Any, Dict, List, Optional, Tuple
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.WebSearchModule.Application.use_cases.web_search_use_case import WebSearch
from src.Common.Chunking.Application.persistence_service import ChunkPersistenceService
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from ..RankingModule.Application.hybrid_search import FusionService  
from src.DI.Config.settings import Settings
from .fallback_helpers import filter_good_results, is_local_insufficient, merge_unique


class WebFallbackHybridSearchService:
    """
    Servicio que orquesta la búsqueda web integrada con el sistema de recuperación.

    Extiende la búsqueda híbrida local (FusionService) con fallback a búsqueda web
    cuando los resultados locales son insuficientes.
    
    Responsabilidades:
    1. Obtener resultados locales (dispersos + densos) usando FusionService
    2. Detectar si los resultados locales son insuficientes
    3. Ejecutar búsqueda web como complemento
    4. Procesar e indexar resultados de web search
    5. Combinar resultados locales y web en respuesta final
    """

    def __init__(
        self,
        fusion_service: FusionService,         
        web_search: WebSearch,
        chunk_persistence: ChunkPersistenceService,
        insufficiency_detector: InsufficientResultsDetector,
        settings: Settings = None
    ):
        self.fusion_service = fusion_service
        self.web_search = web_search
        self.chunk_persistence = chunk_persistence
        self.insufficiency_detector = insufficiency_detector
        self.settings = settings or Settings()
        self.good_rrf_threshold = getattr(self.settings, 'good_rrf_threshold', 0.01)
        self.min_content_length = getattr(self.settings, 'min_content_length', 50)

    
    async def search(self, query: str, k: int = 10, user_id: Optional[str] = None) -> List[HybridSearchResult]:
        local_results = await self.fusion_service.hybrid_search(query, k=200, user_id=user_id)
        print(f"Total resultados locales: {len(local_results)}")

        good_local = filter_good_results(local_results, self.good_rrf_threshold, self.min_content_length)
        print(f"Resultados 'buenos' locales: {len(good_local)}")

        # CORRECCIÓN: pasar len(good_local), no local_results
        is_insufficient, web_needed = is_local_insufficient(len(good_local), k)
        print(f"¿Insuficiente? {is_insufficient}, web_needed: {web_needed}")

        if not is_insufficient:
            return good_local[:k]

        # Búsqueda web
        web_hybrids, web_chunks = await self.web_search.fetch_web_results(query, max_results=web_needed)
        if web_chunks:
            asyncio.create_task(self._safe_store_chunks(web_chunks))

        merged = self._merge_unique(good_local, web_hybrids)
        return merged[:k]

    async def _safe_store_chunks(self, chunks):
        try:
            await self.chunk_persistence.store_chunks(chunks)
        except Exception as e:
            print(f"Error indexando chunks web: {e}")

    # ACTUALMENTE SE PONEN DE PRIMERO LOS RESULTADOS WEB (REVISAR)
    def _merge_unique(self, local, web):
        seen = set()
        merged = []
        for item in web:
            if item.url not in seen:
                seen.add(item.url)
                merged.append(item)
        for item in local:
            if item.url not in seen:
                seen.add(item.url)
                merged.append(item)
        return merged