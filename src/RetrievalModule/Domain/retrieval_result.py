from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RetrievalResult:
    """
    Representa un resultado de búsqueda recuperado.
    
    Attributes:
        url: URL del documento
        title: Título del documento
        content: Contenido o snippet relevante
        score: Puntuación de relevancia (log P(Q|D))
        source: Fuente/origen del documento
        snippet: Fragmento destacado del documento (opcional)
    """
    url: str
    title: str
    content: str
    score: float
    source: str
    snippet: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "snippet": self.snippet
        }
    
    def __repr__(self) -> str:
        return (f"RetrievalResult(url={self.url}, title={self.title[:50]}..., "
                f"score={self.score:.4f}, source={self.source})")
