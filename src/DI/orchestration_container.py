from dependency_injector import containers, providers
from src.FeedbackModule.infrastructure.memory_feedback_repository import MemoryFeedbackRepository
from src.FeedbackModule.application.feedback_service import FeedbackService
from src.FeedbackModule.application.refinement_service import RefinementService
from src.Orchestration.web_extended_hybrid_search_service import WebFallbackHybridSearchService

class OrchestrationContainer(containers.DeclarativeContainer):
    # Dependencias externas (se inyectan desde otros contenedores)
    fusion_service = providers.Dependency()
    web_search = providers.Dependency()
    chunk_persistence = providers.Dependency()
    insufficiency_detector = providers.Dependency()
    feedback = providers.Dependency()
    
    # Servicio orquestador
    web_extended_hybrid = providers.Factory(
        WebFallbackHybridSearchService,
        fusion_service=fusion_service,
        web_search=web_search,
        chunk_persistence=chunk_persistence,
        insufficiency_detector=insufficiency_detector,
    )