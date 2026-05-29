from typing import List
from src.Common.Chunking.Application.document_chunk import Chunk
from src.IndexModule.Application.document_processor import ChunkDocumentProcessor
from src.IndexModule.Domain.index_repository import IndexRepository

class IndexService:
    def __init__(
        self,
        repository: IndexRepository,
        chunk_processor: ChunkDocumentProcessor
    ):
        self.repository = repository
        self.chunk_processor = chunk_processor

    async def index_chunks(self, chunks: List[Chunk]) -> None:
        """Indexa una lista de chunks."""
        await self.repository.ensure_index()
        search_docs = [self.chunk_processor.process(chunk) for chunk in chunks]
        await self.repository.index_bulk(search_docs)
        await self.repository.refresh()
