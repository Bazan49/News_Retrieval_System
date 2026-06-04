import logging
from typing import Optional
from src.Common.deduplicate import deduplicate
from src.RAGModule.Application.hybrid_retrieval_service import RetrieverService
from src.RAGModule.Application.rag_generator_service import RAGGeneratorService
from src.RAGModule.Domain.rag_result import RAGResult

logger = logging.getLogger("RAGModule.RAGOrchestratorService")
    
class RAGOrchestratorService:
    """
    Orquesta el pipeline completo de RAG:
    - Recuperación de documentos (con búsqueda híbrida + web + reranking + posicionamiento)
    - Generación de respuesta a partir de los resultados recuperados
    """
    def __init__(
        self,
        retriever: RetrieverService,
        generator: RAGGeneratorService,
    ):
        self.retriever = retriever
        self.generator = generator

    async def search(
        self,
        query: str,
        k: int = 10,
        user_id: Optional[str] = None,
    ) -> RAGResult:
        
        # Recuperar documentos relevantes (ya ordenados)
        hybrid_results = await self.retriever.retrieve(query, k=k, user_id=user_id)

        # Generar respuesta RAG
        logger.info("Generando respuesta RAG")
        answer_text = await self.generator.generate_answer(query, hybrid_results)

        # 2. Filtrar para mostrar solo un chunk por documento (el de mayor final_score)
        unique_sources = deduplicate(hybrid_results)

        logger.info("Resultados únicos por documento (deduplicados) | cantidad=%d", len(unique_sources))

        # Retornar resultado con la respuesta y las fuentes utilizadas
        return RAGResult(query=query, answer=answer_text, sources=unique_sources[:k])
    