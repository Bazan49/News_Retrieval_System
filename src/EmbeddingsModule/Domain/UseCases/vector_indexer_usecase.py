from typing import List, Dict, Any
from src.DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from src.EmbeddingsModule.Domain.chunker import Chunker
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore

class VectorIndexer:
    def __init__(self, chunker: Chunker, embedder: BaseEmbedder, vector_store: BaseVectorStore, batch_size: int = 16):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.batch_size = batch_size

    async def index(self, documents: List[ScrapedDocument]) -> int:
        total_chunks = 0
        batch_ids = []
        batch_texts = []
        batch_metadatas = []

        for doc in documents:
            chunks = self.chunker.chunk(doc)  
            for chunk in chunks:
                batch_ids.append(chunk.id)
                batch_texts.append(chunk.content)
                batch_metadatas.append(chunk.metadata)
                total_chunks += 1

                if len(batch_ids) >= self.batch_size:
                    await self._process_batch(batch_ids, batch_texts, batch_metadatas)
                    batch_ids, batch_texts, batch_metadatas = [], [], []

        # Procesar el último lote
        if batch_ids:
            await self._process_batch(batch_ids, batch_texts, batch_metadatas)

        return total_chunks

    async def _process_batch(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        embeddings = await self.embedder.encode(texts)
        await self.vector_store.add(ids=ids, embeddings=embeddings, documents=texts, metadata=metadatas)