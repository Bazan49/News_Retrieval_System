from abc import ABC, abstractmethod
from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult

class BaseGenerator(ABC):
    @abstractmethod
    async def generate(self, query: str, documents: List[RetrievalResult]) -> str:
        """Genera respuesta basada en la consulta y los documentos recuperados."""
        pass