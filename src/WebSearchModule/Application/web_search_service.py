from typing import Any, Dict, List, Optional
from WebSearchModule.Domain.web_search_repository import WebSearchRepository
from WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from WebSearchModule.Infrastructure.web_search_document_processor import WebSearchDocumentProcessor
from IndexModule.Domain.index_repository import IndexRepository
from RetrievalModule.Domain.retrieval_result import RetrievalResult


class WebSearchService:
    """
    Servicio que orquesta la búsqueda web integrada con el sistema de recuperación.
    
    Responsabilidades:
    1. Detectar si los resultados locales son insuficientes
    2. Ejecutar búsqueda web como complemento
    3. Procesar e indexar resultados de web search
    4. Combinar resultados locales y web en respuesta final
    """
    
    def __init__(
        self,
        web_search_repo: WebSearchRepository,
        insufficiency_detector: InsufficientResultsDetector,
        document_processor: WebSearchDocumentProcessor,
        index_repository: IndexRepository
    ):
        """
        Inicializa el servicio de búsqueda web.
        
        Args:
            web_search_repo: Repositorio de búsqueda web (ej: Google News RSS)
            insufficiency_detector: Detector de insuficiencia de resultados
            document_processor: Processor para convertir a SearchDocument
            index_repository: Repositorio de índice para almacenar resultados
        """
        self.web_search_repo = web_search_repo
        self.insufficiency_detector = insufficiency_detector
        self.document_processor = document_processor
        self.index_repository = index_repository
    
    async def search_with_fallback(
        self,
        query: str,
        local_results: List[Dict[str, Any]],
        web_results_limit: int = 5,
        insufficiency_threshold: float = 0.5,
        store_web_results: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecuta búsqueda local y activa búsqueda web si es necesario.
        
        Args:
            query: Consulta del usuario
            local_results: Resultados recuperados del índice local
            web_results_limit: Máximo de resultados web a obtener
            insufficiency_threshold: Umbral para activar búsqueda web (0-1)
            store_web_results: Si True, indexa los resultados de web search
            
        Returns:
            Dict con:
               - local_results: Resultados del índice local
               - web_results: Resultados de búsqueda web (si aplica)
               - combined_results: Resultados combinados y ordenados
               - web_search_triggered: Boolean indicando si se ejecutó búsqueda web
               - insufficiency_score: Score de insuficiencia
        """
        # 1. Detectar insuficiencia
        insufficiency_score = await self.insufficiency_detector.get_insufficiency_score(
            query, 
            local_results
        )
        is_insufficient = insufficiency_score > insufficiency_threshold
        
        web_results = []
        web_search_triggered = False
        
        # 2. Ejecutar búsqueda web si es necesario
        if is_insufficient:
            web_search_triggered = True
            web_search_entities = await self.web_search_repo.search(
                query, 
                max_results=web_results_limit
            )
            
            # 3. Convertir resultados web a RetrievalResult
            web_results = [
                RetrievalResult(
                    url=entity.link,
                    title=entity.title,
                    content=entity.summary,
                    score=0.0,  # Resultados web tienen score neutral
                    source=entity.source,
                    snippet=entity.summary[:200]
                )
                for entity in web_search_entities
            ]
            
            # 4. Indexar resultados de búsqueda web (almacenamiento)
            if store_web_results and web_search_entities:
                await self._store_web_results(web_search_entities)
        
        # 5. Combinar resultados
        combined_results = self._combine_results(local_results, web_results)
        
        return {
            "local_results": [r.to_dict() if hasattr(r, 'to_dict') else r for r in local_results],
            "web_results": [r.to_dict() if hasattr(r, 'to_dict') else r for r in web_results],
            "combined_results": combined_results,
            "web_search_triggered": web_search_triggered,
            "insufficiency_score": insufficiency_score,
            "total_results": len(combined_results)
        }
    
    async def _store_web_results(self, web_search_entities) -> None:
        """
        Procesa e indexa resultados de búsqueda web.
        
        Args:
            web_search_entities: Entidades WebSearchResult a almacenar
        """
        try:
            # Convertir a SearchDocument
            search_docs = self.document_processor.process_batch(web_search_entities)
            
            # Generar IDs cortos únicos para documentos web
            docs_with_ids = [
                (doc, self.document_processor.generate_short_id(doc.url))
                for doc in search_docs
            ]
            
            # Asegurar índice existe
            await self.index_repository.ensure_index()
            
            # Indexar en lote con IDs personalizados
            await self.index_repository.index_bulk_with_ids(docs_with_ids)
            
            # Refrescar índice
            await self.index_repository.refresh()
        except Exception as e:
            print(f"Error storing web results: {e}")
    
    def _combine_results(
        self, 
        local_results: List[Dict[str, Any]], 
        web_results: List[RetrievalResult]
    ) -> List[Dict[str, Any]]:
        """
        Combina y ordena resultados locales con web.
        
        Estrategia:
        - Resultados locales primero (ya validados)
        - Resultados web después (contexto complementario)
        - Evita duplicados por URL
        
        Args:
            local_results: Resultados del índice local
            web_results: Resultados de búsqueda web
            
        Returns:
            Lista combinada y ordenada
        """
        combined = []
        seen_urls = set()
        
        # Agregar resultados locales
        for result in local_results:
            url = result.get("url", "")
            if url:
                seen_urls.add(url)
                combined.append(result)
        
        # Agregar resultados web sin duplicados
        for result in web_results:
            if result.url not in seen_urls:
                combined.append(result.to_dict())
                seen_urls.add(result.url)
        
        return combined
    
    async def get_query_enhancement_suggestions(self, query: str) -> Dict[str, Any]:
        """
        Sugiere términos adicionales o reformulaciones para búsqueda web.
        Útil para refinar búsquedas web sin modificar la consulta original.
        
        Args:
            query: Consulta original
            
        Returns:
            Sugerencias de búsqueda mejorada
        """
        # Implementación básica: sugerencias simples
        suggestions = {
            "original_query": query,
            "suggested_variants": [
                f"{query} actualidad",
                f"{query} noticias",
                f"{query} últimas noticias",
            ],
            "additional_terms": self._extract_key_terms(query)
        }
        return suggestions
    
    @staticmethod
    def _extract_key_terms(query: str) -> List[str]:
        """
        Extrae términos clave de la consulta (primer paso para expansión).
        
        Args:
            query: Consulta
            
        Returns:
            Lista de términos clave
        """
        # Filtrar palabras comunes
        stop_words = {
            "el", "la", "de", "que", "y", "a", "en", "es", "se",
            "los", "las", "por", "con", "un", "una", "para", "del",
            "al", "este", "esto", "han", "son", "haya", "sea"
        }
        
        terms = [
            t.strip() for t in query.lower().split()
            if len(t.strip()) > 3 and t.lower() not in stop_words
        ]
        return terms
