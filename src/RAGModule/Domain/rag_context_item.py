from dataclasses import dataclass
from typing import Optional

@dataclass
class RAGContextItem:
    """
    Unidad mínima de contexto para el LLM.
    - index: número de orden (1‑based) para referencias cruzadas.
    - title: título del documento.
    - text: contenido del chunk (truncado según límites).
    - source: nombre del dominio (pero útil para citar).
    - date: fecha de publicación (útil para actualidad).
    """
    index: int
    title: str
    text: str
    source: Optional[str] = None
    date: Optional[str] = None
