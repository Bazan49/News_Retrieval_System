from dependency_injector import containers, providers
from src.DI.Config.settings import Settings
from src.Orchestration.web_extended_hybrid_search_service import WebFallbackHybridSearchService

class OrchestrationContainer(containers.DeclarativeContainer):
    # Dependencias externas (se inyectan desde otros contenedores)
    settings = providers.Dependency() #ConfigContainer.settings
    fusion_service = providers.Dependency()
    web_search = providers.Dependency()
    chunk_persistence = providers.Dependency()
    insufficiency_detector = providers.Dependency()
    ranking_service = providers.Dependency()  
    cross_encoder_strategy = providers.Dependency()
    
    # Servicio orquestador
    web_extended_hybrid = providers.Factory(
        WebFallbackHybridSearchService,
        fusion_service=fusion_service,
        web_search=web_search,
        chunk_persistence=chunk_persistence,
        insufficiency_detector=insufficiency_detector,
        ranking_service=ranking_service,
        re_ranking_strategy=cross_encoder_strategy,
        settings=settings
    )