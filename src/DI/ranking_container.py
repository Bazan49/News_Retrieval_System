from datetime import datetime
from dependency_injector import containers, providers
from sentence_transformers import CrossEncoder
from src.RankingModule.Application.ranking_service import RankingService
from src.RankingModule.Infrastructure.cross_encoder_ranking_strategy import CrossEncoderRankingStrategy
from src.RankingModule.Infrastructure.personalization_ranking_strategy import PersonalizationScoringStrategy
from src.RankingModule.Infrastructure.recency_ranking_strategy import RecencyScoringStrategy
from src.RankingModule.Application.hybrid_search import FusionService
from src.RankingModule.Infrastructure.rrf import RRFFusionStrategy

class RankingContainer(containers.DeclarativeContainer):
    # Dependencias externas (se inyectan desde fuera)
    settings = providers.Dependency() #ConfigContainer.settings

    sparse_service = providers.Dependency()
    dense_searcher = providers.Dependency()
    profile_builder = providers.Dependency()
    embedder = providers.Dependency()
    vector_store=providers.Dependency()

    # ---------- Estrategia de fusión ----------

    # ---------- Estrategia de fusión ----------
    fusion_strategy = providers.Singleton(
        RRFFusionStrategy,
        rrf_k=settings.provided.rrf_k,
    )

    fusion_service = providers.Factory(
        FusionService,
        sparse_service=sparse_service,
        dense_searcher=dense_searcher,
        fusion_strategy=fusion_strategy,
    )

    # ---------- Estrategia de re‑ranking ----------

    # Modelo CrossEncoder compartido (singleton)
    cross_encoder_model = providers.Singleton(
        CrossEncoder,
        model_name_or_path=settings.provided.cross_encoder_model_name_or_path,
    )

    cross_encoder_strategy = providers.Singleton(
        CrossEncoderRankingStrategy,
        cross_encoder_model=cross_encoder_model,
    )

    # ---------- Estrategias de scoring ----------

    # Estrategia de frescura (singleton, sin estado)
    recency_scoring_strategy = providers.Singleton(
        RecencyScoringStrategy,
        recency_decay_days=settings.provided.recency_decay_days,
    )

    personalization_scoring_strategy = providers.Singleton(
        PersonalizationScoringStrategy,
        profile_builder=profile_builder,
        embedder=embedder,
        vector_store=vector_store,   # se inyecta desde fuera
    )

     # ---------- Servicio de posicionamiento ----------
    ranking_service = providers.Factory(
        RankingService,
        w_relevance=settings.provided.w_relevance,
        w_personalization=settings.provided.w_personalization,
        w_recency=settings.provided.w_recency,
        w_source=settings.provided.w_source,
        scoring_strategies=providers.List(
            recency_scoring_strategy,
            personalization_scoring_strategy,
        ),
        source_score_local=settings.provided.source_score_local,
        source_score_web=settings.provided.source_score_web,
        activate_cross_encoder=settings.provided.activate_cross_encoder_for_relevance,
    )