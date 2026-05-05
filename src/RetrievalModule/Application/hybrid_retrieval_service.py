import asyncio
from typing import List
from src.RetrievalModule.Application.retrieval_service import RetrievalAppService
from src.EmbeddingsModule.Application.vector_searcher_usecase import VectorSearcher
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult

class HybridRetrievalAppService:
    def __init__(self, sparse_service: RetrievalAppService,
                       dense_searcher: VectorSearcher,
                       rrf_k: int = 60):
        self.sparse_service = sparse_service
        self.dense_searcher = dense_searcher
        self.rrf_k = rrf_k

    async def hybrid_search(self, query: str, k: int = 10) -> List[RetrievalResult]:
        # 1. Ejecutar ambas búsquedas en paralelo
        sparse_task = self.sparse_service.retrieve(query, k=200)
        dense_task = self.dense_searcher.search(query, k=200)

        sparse_results: List[RetrievalResult]
        dense_results: List[RetrievalResult]
        sparse_results, dense_results = await asyncio.gather(sparse_task, dense_task)

        # 2. Calcular puntajes RRF
        rrf_scores = {}

        # Resultados dispersos
        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc.url  
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (self.rrf_k + rank)

        # Resultados densos
        for rank, doc in enumerate(dense_results, start=1):
            doc_id = doc.url
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (self.rrf_k + rank)

        # 3. Ordenar por puntaje RRF y tomar top-k
        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        top_ids = [doc_id for doc_id, _ in ranked[:k]]

        # 4. Construir lista final combinada (objetos RetrievalResult)
        # Creamos un mapa para acceso rápido (puede venir de sparse o dense)
        result_map = {doc.url: doc for doc in sparse_results}
        # Añadir los densos que no estén ya en el mapa (por si algún documento solo aparece en denso)
        for doc in dense_results:
            if doc.url not in result_map:
                result_map[doc.url] = doc

        final_results = [result_map[doc_id] for doc_id in top_ids if doc_id in result_map]
        return final_results