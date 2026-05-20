from abc import ABC, abstractmethod
from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult

class BaseGenerator(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Genera respuesta basada en el prompt del sistema y el prompt del usuario."""
        pass