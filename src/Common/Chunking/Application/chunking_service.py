from typing import List
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument
from src.Common.Chunking.Domain.chunker import Chunker
from src.Common.Chunking.Application.document_chunk import Chunk

class ChunkingService:
    """Servicio de aplicación para fragmentar documentos en chunks."""
    
    def __init__(self, chunker: Chunker):
        self.chunker = chunker

    def chunk_document(self, document: ScrapedDocument) -> List[Chunk]:
        """Fragmenta un documento en una lista de chunks."""
        return self.chunker.chunk(document)

    def chunk_documents(self, documents: List[ScrapedDocument]) -> List[Chunk]:
        """Fragmenta varios documentos y devuelve todos los chunks en una sola lista."""
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunker.chunk(doc))
        return all_chunks