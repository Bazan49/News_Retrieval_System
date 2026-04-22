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
            # Obtener o crear la colección de forma asíncrona
            try:
                self.collection = await self.client.get_collection(name=self.collection_name)
            except Exception:
                self.collection = await self.client.create_collection(name=self.collection_name)

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

    async def delete(self, ids: List[str]) -> None:
        await self._ensure_client()
        await self.collection.delete(ids=ids)
