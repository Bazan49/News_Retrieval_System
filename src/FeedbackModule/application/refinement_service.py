import asyncio
import re
import numpy as np
from typing import List, Optional, Tuple
from keybert import KeyBERT
from src.RAGModule.Domain.rag_result import RAGResult
from src.EmbeddingsModule.Domain.embedder import BaseEmbedder
from src.FeedbackModule.domain.entities import RefinementResult

class RefinementService:
    def __init__(self, embedder: BaseEmbedder, top_n: int = 5):
        self.model = embedder.model   # SentenceTransformer
        self.kw_extractor = KeyBERT(model=self.model)
        self.top_n = top_n

    def _clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str) -> List[str]:
        if not text:
            return []
        if len(text) > 1000:
            text = text[:1000]
        cleaned = self._clean(text)
        n = self.top_n * 2
        keywords = self.kw_extractor.extract_keywords(
            cleaned,
            keyphrase_ngram_range=(1, 1),
            stop_words=None,
            top_n=n
        )
        filtered = []
        seen = set()
        for kw, score in keywords:
            kw_lower = kw.lower()
            if len(kw_lower) < 3 or kw_lower in seen:
                continue
            seen.add(kw_lower)
            filtered.append(kw_lower)
        return filtered[:self.top_n]

    def _extract_keywords_with_scores(self, text: str) -> List[Tuple[str, float]]:
        """Devuelve lista de (keyword, score) para un texto."""
        if not text:
            return []
        if len(text) > 1000:
            text = text[:1000]
        cleaned = self._clean(text)
        n = self.top_n * 2   # candidatos dobles
        keywords = self.kw_extractor.extract_keywords(
            cleaned,
            keyphrase_ngram_range=(1, 1),
            stop_words=None,
            top_n=n
        )
        filtered = []
        for kw, score in keywords:
            if len(kw) >= 3:
                filtered.append((kw, score))
        return filtered

    def expand_query(self, original_query: str, chunk_content: str) -> str:
        keywords = self.extract_keywords(chunk_content)
        if not keywords:
            return original_query

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
        return expanded

    async def expand_query_async(self, original_query: str, chunk_content: str) -> str:
        return await asyncio.to_thread(self.expand_query, original_query, chunk_content)

    async def refine_search(
        self,
        original_query: str,
        chunk_contents: List[str],
        search_service,
        max_chunks: int = 10   # límite de chunks a procesar
    ) -> RefinementResult:
        # Limitar número de chunks para evitar ruido y mejorar rendimiento
        if len(chunk_contents) > max_chunks:
            chunk_contents = chunk_contents[:max_chunks]

        all_keywords = []  # lista de (keyword, score)
        for chunk in chunk_contents:
            kw_scores = self._extract_keywords_with_scores(chunk)
            all_keywords.extend(kw_scores)

        # Ordenar por score descendente
        all_keywords.sort(key=lambda x: x[1], reverse=True)

        # Seleccionar top_n palabras únicas
        seen = set()
        final_keywords = []
        for kw, _ in all_keywords:
            if kw not in seen:
                seen.add(kw)
                final_keywords.append(kw)
            if len(final_keywords) >= self.top_n:
                break

        # Construir consulta expandida
        original_tokens = set(original_query.lower().split())
        new_terms = [kw for kw in final_keywords if kw not in original_tokens]
        expanded_query = f"{original_query} {' '.join(new_terms)}" if new_terms else original_query

        # Ejecutar nueva búsqueda
        new_results = await search_service.search(expanded_query, k=10)
        return RefinementResult(original_query=original_query, expanded_query=expanded_query, results=new_results.sources, answer=new_results.answer)