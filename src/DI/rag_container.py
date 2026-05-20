from dependency_injector import containers, providers
from src.RAGModule.Application.use_cases.context_builder import ContextBuilder
from src.RAGModule.Application.use_cases.prompt_builder import PromptBuilder
from src.RAGModule.Infrastructure.groq_generator import GroqGenerator
from src.RAGModule.Application.rag_service import RAGService
from src.DI.Config.settings import Settings

class RAGContainer(containers.DeclarativeContainer):
    
    settings = providers.Singleton(Settings)

    context_builder = providers.Factory(
        ContextBuilder,
        max_chunks=settings.provided.rag_max_chunks,
        max_chunks_per_doc=settings.provided.rag_max_chunks_per_doc,
    )

    prompt_builder = providers.Factory(PromptBuilder)

    groq_generator = providers.Singleton(
        GroqGenerator,
        api_key=settings.provided.groq_api_key, 
        model_id=settings.provided.groq_model_id,
        temperature=settings.provided.groq_temperature,
        max_tokens=settings.provided.groq_max_tokens,
        frequency_penalty=settings.provided.groq_frequency_penalty,
        presence_penalty=settings.provided.groq_presence_penalty,
        top_p=settings.provided.groq_top_p,
    )

    rag_service = providers.Factory(
        RAGService,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        generator=groq_generator,
    )