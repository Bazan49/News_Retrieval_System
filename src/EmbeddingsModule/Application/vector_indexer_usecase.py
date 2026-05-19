from typing import List, Dict, Any
from src.Common.Chunking.Application.document_chunk import Chunk
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore

class VectorIndexer:
    def __init__(self, embedder: BaseEmbedder, vector_store: BaseVectorStore, batch_size: int = 16):
        self.embedder = embedder
        self.vector_store = vector_store
        self.batch_size = batch_size

    async def index_chunks(self, chunks: List[Chunk]) -> int:
        total_chunks = 0
        batch_ids = []
        batch_texts = []
        batch_metadatas = []

        for chunk in chunks:
            batch_ids.append(chunk.chunk_id)
            batch_texts.append(chunk.content)
            batch_metadatas.append(chunk.metadata.to_dict())
            total_chunks += 1

            if len(batch_ids) >= self.batch_size:
                await self._process_batch(batch_ids, batch_texts, batch_metadatas)
                batch_ids, batch_texts, batch_metadatas = [], [], []

        if batch_ids:
            await self._process_batch(batch_ids, batch_texts, batch_metadatas)

        return total_chunks

    async def _process_batch(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        embeddings = await self.embedder.encode(texts)
        await self.vector_store.add(ids=ids, embeddings=embeddings, documents=texts, metadata=metadatas)

    
    async def delete_chunks(self, chunk_ids: List[str]) -> None:
        """Elimina chunks de ChromaDB por sus IDs."""
        if not chunk_ids:
            return
        await self.vector_store.delete(chunk_ids)