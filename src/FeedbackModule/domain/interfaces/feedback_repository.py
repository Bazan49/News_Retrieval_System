from abc import ABC, abstractmethod
from typing import List, Optional
from src.FeedbackModule.domain.entities import Feedback

class FeedbackRepository(ABC):
    """Interfaz para el repositorio de feedbacks (persistencia)."""

    @abstractmethod
    async def save(self, feedback: Feedback) -> None:
        """Guarda un feedback."""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 1000) -> List[Feedback]:
        """Obtiene todos los feedbacks (sin filtrar)."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 500) -> List[Feedback]:
        """Obtiene feedbacks de un usuario específico."""
        pass

    @abstractmethod
    async def get_all_positive(self, limit: int = 500) -> List[Feedback]:
        """Obtiene todos los feedbacks positivos (likes)."""
        pass

    @abstractmethod
    async def get_all_negative(self, limit: int = 500) -> List[Feedback]:
        """Obtiene todos los feedbacks negativos (dislikes)."""
        pass