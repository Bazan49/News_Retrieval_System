import asyncio
from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.WebSearchModule.Application.use_cases.web_search_use_case import WebSearch
from src.Common.Chunking.Application.persistence_service import ChunkPersistenceService
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from ..RankingModule.Application.hybrid_search import FusionService  

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
    ):
        self.fusion_service = fusion_service
        self.web_search = web_search
        self.chunk_persistence = chunk_persistence
        self.insufficiency_detector = insufficiency_detector

    async def search(self, query: str, k: int = 10) -> List[HybridSearchResult]:
        # 1. Resultados locales (ya fusionados)
        local_results = await self.fusion_service.hybrid_search(query, k=200)

        # 2. Evaluar suficiencia (usando el detector)
        # MEDINA LLAMA AQUI AL DETECTOR PARA EVALUAR SI LOS RESULTADOS LOCALES SON SUFICIENTES
        is_insufficient = True

        if not is_insufficient:
            return local_results[:k]
        
        #DEL DETECTOR RETORNA LA CANTIDAD DE RESULTADOS A BUSCAR EN LA WEB, HAY Q HACER UN 
        #ANALISIS SEGUN LO Q SE TIENE
        web_max_results = 2  # Número máximo de resultados web a recuperar

        # 3. Búsqueda web
        web_hybrids, web_chunks = await self.web_search.fetch_web_results(query, max_results=web_max_results)

        # 4. Indexar chunks web en segundo plano
        if web_chunks:
            asyncio.create_task(self._safe_store_chunks(web_chunks))

        # 5. Combinar 
        return self._merge_unique(local_results, web_hybrids)[:k + len(web_hybrids)]

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