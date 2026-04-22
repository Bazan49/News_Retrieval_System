import asyncio
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder

class SentenceTransformerEmbedder(BaseEmbedder):
    """Implementación concreta de BaseEmbedder utilizando SentenceTransformer."""

    def __init__(self, model_name: str, backend: str = None):
        if backend:
            self.model = SentenceTransformer(model_name, backend=backend)
        else:
            self.model = SentenceTransformer(model_name)

    async def encode(self, texts: List[str]) -> np.ndarray:
        # Ejecutar el encode bloqueante en un hilo separado
        return await asyncio.to_thread(self.model.encode, texts)
    
    async def encode_single(self, text: str) -> np.ndarray:
        return await self.encode([text])  # Shape (1, dim)
    
    async def dim(self) -> int:
        return await asyncio.to_thread(self.model.get_sentence_embedding_dimension)
