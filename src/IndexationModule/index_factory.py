"""
index_factory.py

Fábrica para crear y gestionar índices por tipo de contenido.
"""

from typing import Any, Dict, List, Optional, Type
from .base_index import BaseIndex
from .text_index import TextIndex
from .image_index import ImageIndex


class IndexFactory:
    """Fábrica para crear índices según el tipo de contenido."""
    
    _index_types: Dict[str, Type[BaseIndex]] = {
        'text': TextIndex,
        'image': ImageIndex,
    }
    
    _instances: Dict[str, BaseIndex] = {}
    
    @classmethod
    def get_index(cls, content_type: str, use_existing: bool = True) -> BaseIndex:
        content_type = (content_type or 'text').lower()
        
        if use_existing and content_type in cls._instances:
            return cls._instances[content_type]
        
        index_class = cls._index_types.get(content_type)
        
        if index_class is None:
            raise ValueError(f"Tipo de índice '{content_type}' no soportado")
        
        instance = index_class()
        
        if use_existing:
            cls._instances[content_type] = instance
        
        return instance
    
    @classmethod
    def register_index(cls, content_type: str, index_class: Type[BaseIndex]) -> None:
        """Registrar un nuevo tipo de índice."""
        cls._index_types[content_type.lower()] = index_class
    
    @classmethod
    def get_all_indexes(cls) -> Dict[str, BaseIndex]:
        """Obtener todas las instancias de índices."""
        return cls._instances.copy()
    
    @classmethod
    def clear_all(cls) -> None:
        """Limpiar todas las instancias."""
        cls._instances.clear()
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Obtener tipos de índice soportados."""
        return list(cls._index_types.keys())
