from abc import ABC, abstractmethod
from typing import List, Tuple
from src.FeedbackModule.domain.entities import Feedback

class ProfileRepository(ABC):
    @abstractmethod
    async def get_user_feedbacks(self, user_id: str) -> List[Feedback]:
        """Obtiene todos los feedbacks (likes/dislikes) del usuario."""
        pass