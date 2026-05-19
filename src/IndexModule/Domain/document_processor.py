from src.IndexModule.Domain.search_document import SearchDocument
from src.Common.Chunking.Application.document_chunk import Chunk

class ChunkDocumentProcessor:
    """Procesador para convertir Chunk a SearchDocument"""
    def process(self, chunk: Chunk) -> SearchDocument:
        return SearchDocument(
            chunk_id=chunk.chunk_id,
            url=chunk.metadata.doc_id,
            source=chunk.metadata.source,
            title=chunk.metadata.title,
            content=chunk.content,
            authors=chunk.metadata.authors,
            date=chunk.metadata.publication_date, 
            chunk_number=chunk.metadata.chunk_number,
        )
    