from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DocumentData:
    url: str
    title: str
    content: str
    source: str
    authors: Optional[List[str]]
    date: Optional[str]
    
class RetrieverRepository(ABC):
    """
    Interfaz abstracta para modelo de recuperación.
    
    """
    
    @abstractmethod
    async def get_candidate_documents(self, query_terms: List[str], top_n: int = 100) -> List[DocumentData]:
        """Retorna documentos que contengan al menos un término de la consulta.
           Cada documento incluye: id, title, content, length (número de términos), y term_freqs."""
        pass
