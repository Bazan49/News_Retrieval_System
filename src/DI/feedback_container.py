from dependency_injector import containers, providers
from src.FeedbackModule.infrastructure.sqlite_feedback_repository import SQLiteFeedbackRepository
from src.FeedbackModule.application.feedback_service import FeedbackService
from src.FeedbackModule.application.refinement_service import RefinementService

class FeedbackContainer(containers.DeclarativeContainer):

    settings = providers.Dependency() #ConfigContainer.settings
    
    # Dependencia externa: embedder 
    embedder = providers.Dependency()
    
    feedback_repository = providers.Singleton(SQLiteFeedbackRepository, db_path=settings.provided.feedback_db_path)
    feedback_service = providers.Factory(FeedbackService, repository=feedback_repository)
    
    refinement_service = providers.Singleton(
        RefinementService,
        embedder=embedder,
        top_n=settings.provided.refinement_top_n
    )