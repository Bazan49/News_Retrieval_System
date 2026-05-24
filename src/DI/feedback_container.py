from dependency_injector import containers, providers
from src.DI.Config.settings import Settings
from src.FeedbackModule.infrastructure.memory_feedback_repository import MemoryFeedbackRepository
from src.FeedbackModule.application.feedback_service import FeedbackService
from src.FeedbackModule.application.refinement_service import RefinementService

class FeedbackContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)
    feedback_repository = providers.Singleton(MemoryFeedbackRepository)
    feedback_service = providers.Factory(FeedbackService, repository=feedback_repository)
    refinement_service = providers.Singleton(
        RefinementService,
        model_name=settings.provided.refinement_model_name,
        top_n=settings.provided.refinement_top_n
    )