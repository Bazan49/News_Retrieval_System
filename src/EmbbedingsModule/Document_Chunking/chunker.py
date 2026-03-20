from abc import ABC, abstractmethod
from typing import List
from .document_chunk import Chunk
from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument

class Chunker(ABC):
    """Interfaz de chunker (estrategia de chunking)."""

    @abstractmethod
    def chunk(self, document: ScrapedDocument) -> List[Chunk]:
        """Toma un documento completo y lo divide en chunks con metadata."""
        pass
