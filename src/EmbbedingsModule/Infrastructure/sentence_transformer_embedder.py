from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.EmbbedingsModule.Domain.embedder import BaseEmbedder

class SentenceTransformerEmbedder(BaseEmbedder):
    """Implementación concreta con multilingual-e5-large."""
    
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts)
        return embeddings 
    
    def encode_single(self, text: str) -> np.ndarray:
        return self.encode([text])  # Shape (1, dim)
    
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
