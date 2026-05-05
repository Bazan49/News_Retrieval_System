from typing import List, Dict, Any
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult
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
            # Convertir distancia a score (similitud aproximada)
            score = 1 - (raw['distances'][idx] / 2) if raw['distances'] else None
            result = RetrievalResult(
                doc_id=doc_id,
                url=raw['metadatas'][idx].get('doc_id', ''),
                title=raw['metadatas'][idx].get('title', ''),
                content=raw['documents'][idx],
                score=score,
                source=raw['metadatas'][idx].get('source', ''),
                snippet=snippet,
                authors=authors,
                date=date_str
            )
            results.append(result)
        return results