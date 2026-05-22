from typing import List, Dict, Any
from tqdm import tqdm 
from src.Common.Chunking.Application.document_chunk import Chunk
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.EmbeddingsModule.Domain.vector_store import BaseVectorStore

class VectorIndexer:
    def __init__(self, embedder: BaseEmbedder, vector_store: BaseVectorStore, batch_size: int = 100):
        self.embedder = embedder
        self.vector_store = vector_store
        self.batch_size = batch_size

    async def index_chunks(self, chunks: List[Chunk]) -> int:
        total_chunks = len(chunks)
        if total_chunks == 0:
            return 0

        batch_ids = []
        batch_texts = []
        batch_metadatas = []
        processed = 0

        # Crear la barra de progreso
        with tqdm(total=total_chunks, desc="Indexando chunks", unit="chunk") as pbar:
            for chunk in chunks:
                batch_ids.append(chunk.chunk_id)
                batch_texts.append(chunk.content)
                batch_metadatas.append(chunk.metadata.to_dict())
                processed += 1

                # Cuando se llena el batch o es el último chunk
                if len(batch_ids) >= self.batch_size or processed == total_chunks:
                    await self._process_batch(batch_ids, batch_texts, batch_metadatas)
                    # Actualizar la barra con la cantidad de chunks de este batch
                    pbar.update(len(batch_ids))
                    # Reiniciar el batch
                    batch_ids, batch_texts, batch_metadatas = [], [], []

        return total_chunks

    async def _process_batch(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        embeddings = await self.embedder.encode(texts)
        await self.vector_store.add(ids=ids, embeddings=embeddings, documents=texts, metadata=metadatas)

    async def delete_chunks(self, chunk_ids: List[str]) -> None:
        if not chunk_ids:
            return
        await self.vector_store.delete(chunk_ids)