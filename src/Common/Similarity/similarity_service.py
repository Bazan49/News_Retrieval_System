# src/Common/Similarity/similarity_service.py
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer, util

class SimilarityService:
    """Servicio centralizado para calcular similitud semántica entre textos."""

    def __init__(self, model: SentenceTransformer):
        """
        Args:
            model: Modelo de embeddings ya cargado (por ejemplo, desde RefinementService o EmbeddingsModule)
        """
        self.model = model

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula la similitud coseno entre dos textos."""
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        return util.cos_sim(emb1, emb2).item()

    def cosine_similarity_batch(self, text: str, candidates: List[str]) -> List[float]:
        """Calcula la similitud entre un texto y una lista de candidatos."""
        emb_text = self.model.encode(text)
        emb_candidates = self.model.encode(candidates)
        similarities = util.cos_sim(emb_text, emb_candidates)[0]
        return similarities.tolist()