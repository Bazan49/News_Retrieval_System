"""
base_index.py

Clase abstracta base para todos los índices.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseIndex(ABC):
    """Clase abstracta base para todos los tipos de índices."""
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
    
    @abstractmethod
    def add_document(self, doc_id: str, content: Any, metadata: Optional[Dict] = None) -> None:
        """Agregar un documento al índice."""
        pass
    
    @abstractmethod
    def search(self, query: Any, top_k: int = 10) -> List[Dict]:
        """Buscar documentos relevantes."""
        pass
    
    @abstractmethod
    def remove_document(self, doc_id: str) -> bool:
        """Eliminar un documento del índice."""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Obtener un documento por su ID."""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict) -> None:
        """Cargar el índice desde un diccionario."""
        pass
    
    def count(self) -> int:
        """Cantidad de documentos en el índice."""
        return len(self.documents)
    
    def get_all_documents(self) -> List[Dict]:
        """Obtener todos los documentos."""
        return list(self.documents.values())
    
    def clear(self) -> None:
        """Limpiar todos los documentos."""
        self.documents.clear()
    
    def to_dict(self) -> Dict:
        """Serializar el índice a diccionario."""
        return {
            'type': self.__class__.__name__,
            'document_count': len(self.documents),
            'documents': self.documents
        }
