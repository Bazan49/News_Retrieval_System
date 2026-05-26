from datetime import datetime
from dependency_injector import containers, providers
from src.Common.Similarity.similarity_service import SimilarityService
from src.DI.feedback_container import FeedbackContainer
from src.RankingModule.Infrastructure.feedback_ranking_strategy import FeedbackRankingStrategy
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

    # Servicio de similitud (usa el modelo de refinement_service de FeedbackContainer)
    similarity_service = providers.Factory(
        SimilarityService,
        model=FeedbackContainer.refinement_service.provided.model
    )

    fusion_strategy = providers.Singleton(RRFFusionStrategy, rrf_k=60)

    feedback_ranking_strategy = providers.Factory(
        FeedbackRankingStrategy,
        feedback_repo=FeedbackContainer.feedback_repository,
        refinement_service=FeedbackContainer.refinement_service,
        similarity_service=similarity_service,
        boost_factor=0.3,
        penalty_factor=0.5,
        recency_weight=0.2,
        recency_decay_days=30,
        current_date=datetime.now()
    )

    personalized_ranking_strategy = providers.Factory(
        PersonalizedRankingStrategy,
        profile_builder=profile_builder,
        embedder=embedder,
        personalization_weight=0.4
    )

    ranking_strategies = providers.List(
        feedback_ranking_strategy,
        personalized_ranking_strategy
    )

    fusion_service = providers.Factory(
        FusionService,
        sparse_service=sparse_service,
        dense_searcher=dense_searcher,
        fusion_strategy=fusion_strategy,
        ranking_strategies=ranking_strategies
    )