from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .retrieval_result import RetrievalResult


class RetrieverRepository(ABC):
    """
    Interfaz abstracta para modelo de recuperación.
    
    """
    
    @abstractmethod
    async def get_candidate_documents(self, query_terms: List[str], top_n: int = 100) -> List[Dict[str, Any]]:
        """Retorna documentos que contengan al menos un término de la consulta.
           Cada documento incluye: id, title, content, length (número de términos), y term_freqs."""
        pass
