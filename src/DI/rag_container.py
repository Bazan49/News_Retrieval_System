from dependency_injector import containers, providers
from src.RAGModule.Application.hybrid_retrieval_service import RetrieverService
from src.RAGModule.Application.rag_orchestrator_service import RAGOrchestratorService
from src.RAGModule.Application.use_cases.context_builder import ContextBuilder
from src.RAGModule.Application.use_cases.prompt_builder import PromptBuilder
from src.RAGModule.Infrastructure.groq_generator import GroqGenerator
from src.RAGModule.Application.rag_generator_service import RAGGeneratorService

class RAGContainer(containers.DeclarativeContainer):
    
    settings = providers.Dependency() #ConfigContainer.settings

    # Dependencias externas para el recuperador
    fusion_service = providers.Dependency()
    ranking_service = providers.Dependency()
    re_ranking_strategy = providers.Dependency()
    web_search = providers.Dependency()
    chunk_persistence = providers.Dependency()
    insufficiency_detector = providers.Dependency()

    # ---- Recuperador ----
    retriever_service = providers.Factory(
        RetrieverService,
        fusion_service=fusion_service,
        ranking_service=ranking_service,
        re_ranking_strategy=re_ranking_strategy,
        web_search=web_search,
        chunk_persistence=chunk_persistence,
        insufficiency_detector=insufficiency_detector,
        activate_reranking=settings.provided.activate_cross_encoder_for_relevance,
    )

    # ---- Generador de respuesta ----
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

    rag_generator = providers.Factory(
        RAGGeneratorService,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        generator=groq_generator,
    )

    # ---- Orquestador RAG completo ----
    rag_orchestrator = providers.Factory(
        RAGOrchestratorService,
        retriever=retriever_service,
        generator=rag_generator,
    )