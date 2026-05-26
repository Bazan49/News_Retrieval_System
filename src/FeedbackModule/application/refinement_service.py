import re
from typing import List, Optional
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

from src.FeedbackModule.domain.entities import RefinementResult

class RefinementService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", top_n: int = 5):
        print(f"[RefinementService] Cargando modelo '{model_name}'...")
        self.model = SentenceTransformer(model_name)
        self.kw_extractor = KeyBERT(model=self.model)
        self.top_n = top_n
        print("[RefinementService] Inicialización completada.")

    def _clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str, top_n: Optional[int] = None) -> List[str]:
        if not text:
            return []
        # Limitar la longitud del texto a 1000 caracteres para velocidad
        if len(text) > 1000:
            text = text[:1000]
        cleaned = self._clean(text)
        n = top_n if top_n is not None else self.top_n
        # Extraer el doble de candidatos para luego filtrar
        keywords = self.kw_extractor.extract_keywords(
            cleaned,
            keyphrase_ngram_range=(1, 1),   # palabras individuales
            stop_words= "english",
            top_n=n * 2
        )
        # Filtrar palabras cortas
        filtered = []
        seen = set()
        for kw, score in keywords:
            kw_lower = kw.lower()
            if len(kw_lower) < 3 or kw_lower in seen:
                continue
            seen.add(kw_lower)
            filtered.append(kw_lower)
        return filtered[:n]

    def expand_query(self, original_query: str, chunk_content: str, top_n: Optional[int] = None) -> str:
        n = top_n if top_n is not None else self.top_n
        keywords = self.extract_keywords(chunk_content, top_n=n)
        if not keywords:
            return original_query

        original_tokens = set(original_query.lower().split())
        new_terms = []
        for kw in keywords:
            if kw not in original_tokens and kw not in new_terms:
                new_terms.append(kw)
            if len(new_terms) >= n:
                break

        if not new_terms:
            return original_query

        expanded = f"{original_query} {' '.join(new_terms)}"
        return expanded
    
    async def refine_search(self, original_query: str, chunk_content: str, top_n: Optional[int], search_service) -> RefinementResult:
        expanded_query = self.expand_query(original_query, chunk_content, top_n=top_n)
        new_results = await search_service.hybrid_search(expanded_query, k=10)
        return RefinementResult(original_query=original_query, expanded_query=expanded_query, results=new_results)