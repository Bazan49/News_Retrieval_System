import logging
from typing import List
from src.Common.Chunking.Application.document_chunk import Chunk
from src.EmbeddingsModule.Application.vector_indexer_usecase import VectorIndexer
from src.IndexModule.Application.index_service import IndexService

logger = logging.getLogger("ChunkPersistenceService")

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
            logger.info("ChromaDB: indexación completada | chunks_indexados=%d", total)
        except Exception as e:
            logger.error("Error durante la indexación en ChromaDB | error=%s", str(e), exc_info=True)
            return 0  # No se continúa

        # 2. Indexar en Elasticsearch
        try:
            await self.index_service.index_chunks(chunks)
            logger.info("Elasticsearch: indexación completada | chunks_indexados=%d", len(chunks))
            return total
        except Exception as e:
            logger.error("Error durante la indexación en Elasticsearch | error=%s", str(e), exc_info=True)
            # 3. Compensación: eliminar los chunks de ChromaDB
            chunk_ids = [c.chunk_id for c in chunks]
            logger.info("Elasticsearch: error en la indexación | deshaciendo cambios en ChromaDB | chunks_a_eliminar=%d", len(chunk_ids))
            try:
                await self.vector_indexer.delete_chunks(chunk_ids)
                logger.info("Compensación completada: chunks eliminados de ChromaDB.")
            except Exception as rollback_error:
                logger.error("Falló la compensación en ChromaDB: %s", str(rollback_error), exc_info=True)
            raise  # Re-lanzar la excepción