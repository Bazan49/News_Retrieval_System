from datetime import datetime

from dependency_injector import containers, providers
from src.Common.Similarity.similarity_service import SimilarityService
from src.DI.feedback_container import FeedbackContainer
from src.RankingModule.Infrastructure.feedback_ranking_strategy import FeedbackRankingStrategy
from src.RankingModule.Application.hybrid_search import FusionService
from src.RankingModule.Infrastructure.rrf import RRFFusionStrategy

class RankingContainer(containers.DeclarativeContainer):

    # Declarar las dependencias externas (se inyectarán desde fuera)
    sparse_service = providers.Dependency()
    dense_searcher = providers.Dependency()

    similarity_service = providers.Factory(
        SimilarityService,
        model=FeedbackContainer.refinement_service.provided.model
    )

    # Estrategia de fusión 
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

    # Servicio de fusión que depende de las anteriores
    fusion_service = providers.Factory(
        FusionService,
        sparse_service=sparse_service,
        dense_searcher=dense_searcher,
        fusion_strategy=fusion_strategy,
        ranking_strategy=feedback_ranking_strategy 
    )
