from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from unicodedata import name
import numpy as np


class BaseVectorStore(ABC):
    """Interfaz para almacenamiento vectorial (domain)."""
    
    @abstractmethod
    async def add(
        self, 
        ids: List[str],
        embeddings: np.ndarray,
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """Añade vectores con metadatos."""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        """Búsqueda de similitud."""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Elimina vectores por IDs."""
        pass
    