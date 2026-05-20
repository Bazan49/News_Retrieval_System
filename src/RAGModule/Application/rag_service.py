from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.RAGModule.Application.use_cases.context_builder import ContextBuilder
from src.RAGModule.Application.use_cases.prompt_builder import PromptBuilder
from src.RAGModule.Domain.generator import BaseGenerator
from src.RAGModule.Domain.rag_result import RAGResult

class RAGService:

    """
    Servicio de Generación Aumentada por Recuperación (RAG).
    
    Responsabilidad: Dada una consulta y una lista de resultados híbridos, 
    construye el contexto, lo formatea, genera un prompt y llama al LLM
    para obtener una respuesta. Devuelve la respuesta junto con las fuentes utilizadas
    (los mismos objetos HybridSearchResult seleccionados).
    """
    
    def __init__(
        self,
        context_builder: ContextBuilder,
        prompt_builder: PromptBuilder,
        generator: BaseGenerator,
    ):
        """
        Args:
            context_builder: Construye y formatea el contexto a partir de los resultados.
            prompt_builder: Construye el system y user prompts.
            generator: Generador de texto (ej. GroqGenerator) que recibe (system, user).
        """
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.generator = generator

    async def answer(
        self,
        query: str,
        hybrid_results: List[HybridSearchResult]
    ) -> RAGResult:
        
        # 1. Construir contexto formateado y obtener los HybridSearchResult seleccionados
        context_str = self.context_builder.build(hybrid_results)

        # 2. Construir system y user prompts
        system_prompt, user_prompt = self.prompt_builder.build(query, context_str)

        # 3. Generar respuesta con el LLM
        answer_text = await self.generator.generate(system_prompt, user_prompt)

        # 4. Retornar resultado con las fuentes originales (HybridSearchResult)
        return RAGResult(query=query, answer=answer_text, sources=hybrid_results)