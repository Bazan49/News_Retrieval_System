"""
IndexationModule

Módulo de indexación para el sistema de recuperación de información.

Submódulos:
- base_index: Clase abstracta base para índices
- text_index: Índice invertido para contenido textual
- image_index: Índice para metadatos de imágenes
- index_factory: Fábrica para crear índices por tipo
- text_normalizer: Procesamiento y normalización de texto
"""

from .base_index import BaseIndex
from .text_index import TextIndex
from .image_index import ImageIndex
from .index_factory import IndexFactory
from .text_normalizer import TextNormalizer

__all__ = [
    'BaseIndex',
    'TextIndex',
    'ImageIndex',
    'IndexFactory',
    'TextNormalizer',
]
