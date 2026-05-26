from dependency_injector import containers, providers
from src.FeedbackModule.infrastructure.sqlite_feedback_repository import SQLiteFeedbackRepository
from src.EmbeddingsModule.Application.vector_searcher_usecase import VectorSearcher
from src.RecommendationModule.Infrastructure.sqlite_search_history_repository import SQLiteSearchHistoryRepository
from src.RecommendationModule.Application.user_profile_builder import UserProfileBuilder
from src.RecommendationModule.Application.content_based_recommender import ContentRecommender

class RecommendationContainer(containers.DeclarativeContainer):
    feedback_repo = providers.Dependency()
    embedder = providers.Dependency()
    vector_searcher = providers.Dependency()

    search_history_repo = providers.Singleton(SQLiteSearchHistoryRepository, db_path="search_history.db")

    profile_builder = providers.Factory(
        UserProfileBuilder,
        feedback_repo=feedback_repo,
        search_history_repo=search_history_repo,
        embedder=embedder,
        like_weight=1.0,
        dislike_weight=-0.5,
        max_queries=20,
        profile_cache_ttl=300   # 5 minutos
    )

    content_recommender = providers.Factory(
        ContentRecommender,
        profile_builder=profile_builder,
        vector_searcher=vector_searcher,
        recency_weight=0.2,
        recency_decay_days=30
    )