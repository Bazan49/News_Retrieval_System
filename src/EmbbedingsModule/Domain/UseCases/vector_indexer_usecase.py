from typing import List, Dict, Any
from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument
from EmbbedingsModule.Domain.chunker import Chunker
from EmbbedingsModule.Domain.embedder import BaseEmbedder
from EmbbedingsModule.Domain.vector_store import BaseVectorStore
import numpy as np


class VectorIndexer:
    """Use case: ScrapedDocument → Chunks → Embeddings → VectorStore."""
    
    def __init__(
        self,
        chunker: Chunker,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore
    ):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
    
    def index(self, documents: List[ScrapedDocument]) -> int:
        """Indexación completa."""
        total_chunks = 0
        
        for doc in documents:
            # 1. Chunking (ScrapedDocument → List[Chunk])
            chunks = self.chunker.chunk(doc)
            
            # 2. Preparar datos
            ids = [chunk.id for chunk in chunks]
            texts = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            
            # 3. Embeddings (np.ndarray)
            embeddings = self.embedder.encode(texts)
            
            # 4. Vector store
            self.vector_store.add(ids, embeddings, texts, metadatas)
            total_chunks += len(chunks)
        
        return total_chunks
