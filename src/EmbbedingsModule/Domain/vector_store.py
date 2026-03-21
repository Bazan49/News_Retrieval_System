from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np


class BaseVectorStore(ABC):
    """Interfaz para almacenamiento vectorial (domain)."""
    
    @abstractmethod
    def add(
        self, 
        ids: List[str],
        embeddings: np.ndarray,
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """Añade vectores con metadatos."""
        pass
    
    @abstractmethod
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        """Búsqueda de similitud."""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Elimina vectores por IDs."""
        pass
    
    @abstractmethod
    def update(
        self,
        ids: List[str],
        embeddings: Optional[np.ndarray] = None,
        documents: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Actualiza vectores existentes."""
        pass
    
