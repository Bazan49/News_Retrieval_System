from datetime import datetime
from dependency_injector import containers, providers
from src.DI.feedback_container import FeedbackContainer
from src.RankingModule.Infrastructure.personalized_ranking_strategy import PersonalizedRankingStrategy
from src.RankingModule.Application.hybrid_search import FusionService
from src.RankingModule.Infrastructure.rrf import RRFFusionStrategy

class RankingContainer(containers.DeclarativeContainer):
    # Dependencias externas (se inyectan desde fuera)
    sparse_service = providers.Dependency()
    dense_searcher = providers.Dependency()
    
    # Dependencias para la estrategia personalizada (se inyectan desde fuera)
    profile_builder = providers.Dependency()
    embedder = providers.Dependency()


    fusion_strategy = providers.Singleton(RRFFusionStrategy, rrf_k=60)

    personalized_ranking_strategy = providers.Factory(
        PersonalizedRankingStrategy,
        profile_builder=profile_builder,
        embedder=embedder,
        personalization_weight=0.4
    )

    ranking_strategies = providers.List(
        personalized_ranking_strategy
    )

    fusion_service = providers.Factory(
        FusionService,
        sparse_service=sparse_service,
        dense_searcher=dense_searcher,
        fusion_strategy=fusion_strategy,
        ranking_strategies=ranking_strategies
    )