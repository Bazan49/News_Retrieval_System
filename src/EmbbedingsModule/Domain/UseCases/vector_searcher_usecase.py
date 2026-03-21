from typing import List, Dict, Any
from EmbbedingsModule.Domain.embedder import BaseEmbedder
from EmbbedingsModule.Domain.vector_store import BaseVectorStore


class VectorSearcher:
    """Use case: Query → Embedding → Search in VectorStore."""
    
    def __init__(self, embedder: BaseEmbedder, vector_store: BaseVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
    
    def search(self, query: str, k: int = 10, filters: Dict[str, Any] = None) -> Dict[str, List[Any]]:
        """Búsqueda por similitud."""
        query_vector = self.embedder.encode_single(query)
        return self.vector_store.search(query_vector, k, filters)