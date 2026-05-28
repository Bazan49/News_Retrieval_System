import asyncio
import re
import numpy as np
from typing import List, Optional
from keybert import KeyBERT
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.FeedbackModule.domain.entities import RefinementResult

class RefinementService:
    def __init__(self, embedder: BaseEmbedder, top_n: int = 5):
        self.model = embedder.model   # SentenceTransformer
        self.kw_extractor = KeyBERT(model=self.model)
        self.top_n = top_n
        print("[RefinementService] Inicialización completada.")

    def _clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str) -> List[str]:
        if not text:
            return []
        # Limitar la longitud del texto a 1000 caracteres para velocidad
        if len(text) > 1000:
            text = text[:1000]
        cleaned = self._clean(text)
        n = self.top_n
        # Extraer el doble de candidatos para luego filtrar
        keywords = self.kw_extractor.extract_keywords(
            cleaned,
            keyphrase_ngram_range=(1, 1),   # palabras individuales
            stop_words=None,
            top_n=n * 2
        )
        if not keywords:
            return []

        # Filtrar por longitud y deduplicación semántica usando numpy
        filtered = []
        seen_embeddings = []   # lista de arrays numpy (embeddings)
        for kw, score in keywords:
            kw_lower = kw.lower()
            if len(kw_lower) < 3:
                continue
            # Obtener embedding como array numpy (1D)
            emb = self.model.encode(kw_lower, convert_to_numpy=True)
            if seen_embeddings:
                # Calcular similitud coseno con todas las palabras ya aceptadas
                # seen_embeddings: lista de arrays; convertimos a matriz (N, dim)
                stacked = np.vstack(seen_embeddings)   # (N, dim)
                # similitud coseno por filas
                norms = np.linalg.norm(stacked, axis=1)
                sims = np.dot(stacked, emb) / (norms * np.linalg.norm(emb))
                max_sim = sims.max()
                if max_sim < 0.8:   # umbral de redundancia
                    filtered.append(kw_lower)
                    seen_embeddings.append(emb)
            else:
                filtered.append(kw_lower)
                seen_embeddings.append(emb)
            if len(filtered) >= n:
                break
        return filtered

    def expand_query(self, original_query: str, chunk_content: str) -> str:
        print("antes del kw")
        keywords = self.extract_keywords(chunk_content)
        if not keywords:
            return original_query
        print(f"Keywords extraídas para refinamiento: {keywords}")

        original_tokens = set(original_query.lower().split())
        new_terms = []
        for kw in keywords:
            if kw not in original_tokens and kw not in new_terms:
                new_terms.append(kw)
            if len(new_terms) >= self.top_n:
                break

        if not new_terms:
            return original_query

        expanded = f"{original_query} {' '.join(new_terms)}"
        print("casi final")
        return expanded

    async def expand_query_async(self, original_query: str, chunk_content: str) -> str:
        print("holaaa")
        return await asyncio.to_thread(self.expand_query, original_query, chunk_content)

    async def refine_search(self, original_query: str, chunk_content: str, search_service) -> RefinementResult:
        expanded_query = await self.expand_query_async(original_query, chunk_content)
        new_results = await search_service.hybrid_search(expanded_query, k=10)
        return RefinementResult(original_query=original_query, expanded_query=expanded_query, results=new_results)