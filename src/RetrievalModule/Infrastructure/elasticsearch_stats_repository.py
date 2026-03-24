from typing import Dict, Counter
from collections import Counter as CollectionCounter
from elasticsearch import AsyncElasticsearch

from ..Domain.stats_repository import StatsRepository

class ElasticsearchStatsRepository(StatsRepository):
    """
    Implementación de StatsRepository que calcula las estadísticas
    recorriendo todos los documentos de Elasticsearch y tokenizando
    el campo 'content' con el analizador utilizado en la indexación.
    
    """

    def __init__(
        self,
        client: AsyncElasticsearch,
        index_name: str,
        analyzer: str = "spanish_analyzer"
    ):
        self.client = client
        self.index_name = index_name
        self.analyzer = analyzer
        self._initialized = False
        self._doc_term_freqs: Dict[str, CollectionCounter] = {}
        self._doc_lengths: Dict[str, int] = {}
        self._collection_freq: CollectionCounter = CollectionCounter()

    async def _ensure_initialized(self):
        """Calcula las estadísticas si aún no se han calculado."""
        if self._initialized:
            return

        # Usar scroll para recorrer todos los documentos
        scroll_size = 1000
        scroll = "2m"

        response = await self.client.search(
            index=self.index_name,
            body={
                "size": scroll_size,
                "_source": ["content", "title", "url", "source"],
                "query": {"match_all": {}}
            },
            scroll=scroll
        )

        scroll_id = response.get("_scroll_id")
        hits = response.get("hits", {}).get("hits", [])

        while hits:
            for hit in hits:
                doc_id = hit["_id"]
                content = hit["_source"].get("content", "")

                # Tokenizar el contenido usando el mismo analizador
                tokens = await self._tokenize(content)

                # Calcular frecuencia por documento
                doc_counter = CollectionCounter(tokens)
                self._doc_term_freqs[doc_id] = doc_counter
                self._doc_lengths[doc_id] = len(tokens)

                # Acumular frecuencias globales
                for term, tf in doc_counter.items():
                    self._collection_freq[term] += tf

            # Obtener siguiente lote
            response = await self.client.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = response.get("_scroll_id")
            hits = response.get("hits", {}).get("hits", [])

        # Limpiar scroll
        if scroll_id:
            await self.client.clear_scroll(scroll_id=scroll_id)

        self._initialized = True

    async def _tokenize(self, text: str) -> list[str]:
        """Tokeniza el texto usando el analizador de Elasticsearch."""
        if not text:
            return []

        response = await self.client.indices.analyze(
            index=self.index_name,
            body={
                "analyzer": self.analyzer,
                "text": text
            }
        )
        return [token["token"] for token in response["tokens"]]

    async def get_doc_term_freqs(self) -> Dict[str, CollectionCounter]:
        await self._ensure_initialized()
        return self._doc_term_freqs

    async def get_doc_lengths(self) -> Dict[str, int]:
        await self._ensure_initialized()
        return self._doc_lengths

    async def get_collection_freq(self) -> CollectionCounter:
        await self._ensure_initialized()
        return self._collection_freq