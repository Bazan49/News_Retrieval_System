from typing import List
from src.Common.Chunking.Application.document_chunk import Chunk
from src.EmbeddingsModule.Application.vector_indexer_usecase import VectorIndexer
from src.IndexModule.Application.index_service import IndexService

class ChunkPersistenceService:
    def __init__(self, vector_indexer: VectorIndexer, index_service: IndexService):
        self.vector_indexer = vector_indexer
        self.index_service = index_service

    async def store_chunks(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0

        # 1. Indexar en ChromaDB
        try:
            total = await self.vector_indexer.index_chunks(chunks)
            print(f"✅ ChromaDB: {total} chunks indexados correctamente.")
        except Exception as e:
            print(f"❌ Error en ChromaDB: {e}")
            return 0  # No se continúa

        # 2. Indexar en Elasticsearch
        try:
            await self.index_service.index_chunks(chunks)
            print(f"✅ Elasticsearch: {len(chunks)} chunks indexados correctamente.")
            return total
        except Exception as e:
            print(f"❌ Error en Elasticsearch: {e}")
            # 3. Compensación: eliminar los chunks de ChromaDB
            chunk_ids = [c.chunk_id for c in chunks]
            print(f"🔄 Deshaciendo cambios en ChromaDB: eliminando {len(chunk_ids)} chunks...")
            try:
                await self.vector_indexer.delete_chunks(chunk_ids)
                print(f"✅ Compensación completada: chunks eliminados de ChromaDB.")
            except Exception as rollback_error:
                print(f"⚠️ Falló la compensación en ChromaDB: {rollback_error}")
            raise  # Re-lanzar la excepción para que el llamador sepa que falló