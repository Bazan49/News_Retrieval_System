from dependency_injector import containers, providers
from src.FeedbackModule.infrastructure.sqlite_feedback_repository import SQLiteFeedbackRepository
from src.DI.Config.settings import Settings
from src.FeedbackModule.application.feedback_service import FeedbackService
from src.FeedbackModule.application.refinement_service import RefinementService

class FeedbackContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)
    
    # Dependencia externa: embedder 
    embedder = providers.Dependency()
    
    feedback_repository = providers.Singleton(SQLiteFeedbackRepository, db_path="feedback.db")
    feedback_service = providers.Factory(FeedbackService, repository=feedback_repository)
    
    refinement_service = providers.Singleton(
        RefinementService,
        embedder=embedder,
        top_n=settings.provided.refinement_top_n
    )