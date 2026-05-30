import chromadb
from chromadb import AsyncHttpClient
import numpy as np
from typing import List, Dict, Any, Optional
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    async def _ensure_client(self):
        if self.client is None:
            self.client = await chromadb.AsyncHttpClient(host=self.host, port=self.port)
            try:
                self.collection = await self.client.get_collection(name=self.collection_name)
            except Exception:
                # Crear colección con métrica coseno
                self.collection = await self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
            )
                
    async def add(
        self,
        ids: List[str],
        embeddings: np.ndarray,
        documents: List[str],
        metadata: List[Dict[str, Any]],
    ) -> None:
        await self._ensure_client()
        await self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist() if embeddings is not None else None,
            documents=documents,
            metadatas=metadata
        )

    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        await self._ensure_client()
        if query_vector.ndim == 1:
            query_embeddings = [query_vector.tolist()]
        else:
            query_embeddings = query_vector.tolist()

        result = await self.collection.query(
            query_embeddings=query_embeddings,
            n_results=k,
            where=filters,
            include=["documents", "metadatas", "distances", "embeddings"]
        )

        if not result or not result.get("ids"):
            return {"ids": [], "documents": [], "metadatas": [], "distances": [], "embeddings": []}

        return {
            "ids": result["ids"][0],
            "documents": result["documents"][0],
            "metadatas": result["metadatas"][0],
            "distances": result["distances"][0],
            "embeddings": result.get("embeddings", [[]])[0],
        }
    
    async def get_embeddings_by_ids(self, ids: List[str]) -> Dict[str, List[float]]:
        await self._ensure_client()
        result = await self.collection.get(ids=ids, include=["embeddings"])
        embeddings = result.get("embeddings")
        if embeddings is None:
            return {}
        # Si es un array de NumPy vacío
        if hasattr(embeddings, "size") and embeddings.size == 0:
            return {}
        # Si es una lista vacía
        if len(embeddings) == 0:
            return {}
        return {doc_id: emb for doc_id, emb in zip(result["ids"], embeddings)}

    async def get_embedding_by_id(self, doc_id: str) -> Optional[np.ndarray]:
        """Recupera el embedding de un documento por su ID."""
        embeddings = await self.get_embeddings_by_ids([doc_id])
        if doc_id in embeddings:
            return np.array(embeddings[doc_id])
        return None

    async def delete(self, ids: List[str]) -> None:
        await self._ensure_client()
        await self.collection.delete(ids=ids)
