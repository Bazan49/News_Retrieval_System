from typing import List, Dict, Any

import numpy as np
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore

class VectorSearcher:
    """Use case: Query → Embedding → Search in VectorStore."""
    
    def __init__(self, embedder: BaseEmbedder, vector_store: BaseVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
    
    async def search(self, query: str, k: int = 10, filters: Dict[str, Any] = None) -> Dict[str, List[Any]]:
        """Búsqueda por similitud."""
        query_vector = await self.embedder.encode_single(query)
        raw = await self.vector_store.search(query_vector, k, filters)
        
        results = []
        for idx, doc_id in enumerate(raw.get('ids', [])):
            snippet = raw['documents'][idx][:200] + "..." if len(raw['documents'][idx]) > 200 else raw['documents'][idx]
            # Obtener autores y fecha de metadatos (ajusta las claves según tu almacenamiento)
            authors = raw['metadatas'][idx].get('authors')
            date_str = raw['metadatas'][idx].get('date') or raw['metadatas'][idx].get('publication_date')
            # Obtener score 
            score = raw['distances'][idx] if raw['distances'] else None
            result = RetrievalResult(
                doc_id=doc_id,
                url=raw['metadatas'][idx].get('doc_id', ''),
                title=raw['metadatas'][idx].get('title', ''),
                content=raw['documents'][idx],
                score=score,
                source=raw['metadatas'][idx].get('source', ''),
                snippet=snippet,
                authors=authors,
                date=date_str,
                chunk_number = raw['metadatas'][idx].get('chunk_number')
            )
            results.append(result)
        return results
    
    async def search_by_vector(self, vector: np.ndarray, k: int = 10) -> List[RetrievalResult]:
        """Nuevo: busca documentos similares a un vector dado (útil para recomendación)."""
        raw = await self.vector_store.search(vector, k)
        return self._parse_results(raw)

    def _parse_results(self, raw: Dict) -> List[RetrievalResult]:
        """Lógica común de parseo de resultados de ChromaDB."""
        results = []
        for idx, doc_id in enumerate(raw.get('ids', [])):
            snippet = raw['documents'][idx][:200] + "..." if len(raw['documents'][idx]) > 200 else raw['documents'][idx]
            authors = raw['metadatas'][idx].get('authors')
            date_str = raw['metadatas'][idx].get('date') or raw['metadatas'][idx].get('publication_date')
            score = raw['distances'][idx] if raw['distances'] else None
            result = RetrievalResult(
                doc_id=doc_id,
                url=raw['metadatas'][idx].get('doc_id', ''),
                title=raw['metadatas'][idx].get('title', ''),
                content=raw['documents'][idx],
                score=score,
                source=raw['metadatas'][idx].get('source', ''),
                snippet=snippet,
                authors=authors,
                date=date_str,
                chunk_number=raw['metadatas'][idx].get('chunk_number')
            )
            results.append(result)
        return results