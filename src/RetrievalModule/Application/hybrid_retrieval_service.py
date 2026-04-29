import asyncio
from typing import List, Dict, Any
from src.RetrievalModule.Application.retrieval_service import RetrievalAppService
from src.EmbeddingsModule.Domain.UseCases.vector_searcher_usecase import VectorSearcher

class HybridRetrievalAppService:
    def __init__(self, sparse_service: RetrievalAppService,
                       dense_searcher: VectorSearcher,
                       rrf_k: int = 60):
        self.sparse_service = sparse_service
        self.dense_searcher = dense_searcher
        self.rrf_k = rrf_k

    async def hybrid_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        # 1. Ejecutar ambas búsquedas en paralelo
        sparse_task = self.sparse_service.retrieve(query, k=200)  
        dense_task = self.dense_searcher.search(query, k=200)

        sparse_results, dense_results = await asyncio.gather(sparse_task, dense_task)

        # 2. Calcular puntajes RRF
        rrf_scores = {}

        # Resultados dispersos (LMIR) – cada resultado tiene 'url' como clave
        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc['url']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (self.rrf_k + rank)

        # Resultados densos (ChromaDB) – dense_results tiene 'ids' como lista
        for rank, doc_id in enumerate(dense_results['ids'], start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (self.rrf_k + rank)

        # 3. Ordenar por puntaje RRF descendente y tomar top-k
        ranked_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        top_doc_ids = [doc_id for doc_id, _ in ranked_docs[:k]]

        # 4. Construir respuesta final combinando metadatos de ambas fuentes
        final_results = []
        doc_map = {doc['url']: doc for doc in sparse_results}

        for doc_id in top_doc_ids:
            if doc_id in doc_map:
                final_results.append(doc_map[doc_id])
            else:
                # Buscar en resultados densos si no aparece en dispersos
                idx = dense_results['ids'].index(doc_id)
                final_results.append({
                    'url': doc_id,
                    'title': dense_results['metadatas'][idx].get('title', ''),
                    'content': dense_results['documents'][idx],
                    'score': None,  # puedes calcular un score combinado
                    'source': dense_results['metadatas'][idx].get('source', ''),
                    'snippet': dense_results['documents'][idx][:200] + "..."
                })
        return final_results