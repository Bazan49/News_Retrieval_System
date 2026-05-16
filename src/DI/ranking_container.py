from dependency_injector import containers, providers
from src.RankingModule.Application.hybrid_search import FusionService
from src.RankingModule.Infrastructure.rrf import RRFFusionStrategy

class RankingContainer(containers.DeclarativeContainer):

    # Declarar las dependencias externas (se inyectarán desde fuera)
    sparse_service = providers.Dependency()
    dense_searcher = providers.Dependency()

    # Estrategia de fusión 
    fusion_strategy = providers.Singleton(RRFFusionStrategy, rrf_k=60)

    # Servicio de fusión que depende de las anteriores
    fusion_service = providers.Factory(
        FusionService,
        sparse_service=sparse_service,
        dense_searcher=dense_searcher,
        fusion_strategy=fusion_strategy,
    )