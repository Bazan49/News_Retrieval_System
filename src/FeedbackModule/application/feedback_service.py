from src.FeedbackModule.domain.entities import Feedback
from src.FeedbackModule.infrastructure.memory_feedback_repository import MemoryFeedbackRepository

class FeedbackService:
    def __init__(self, repository: MemoryFeedbackRepository):
        self.repository = repository

    async def add_feedback(self, query: str, chunk_id: str, chunk_content: str, rating: bool, user_id: str = None) -> None:
        feedback = Feedback(
            query=query,
            chunk_id=chunk_id,
            chunk_content=chunk_content,
            rating=rating,
            user_id=user_id
        )
        await self.repository.save(feedback)