from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WebSearchResult:
    """
    Resultado de una búsqueda web recuperado de RSS.
    
    Attributes:
        title: Título del artículo
        link: URL del artículo
        published: Fecha de publicación
        summary: Resumen o descripción del artículo
        source: Fuente del RSS (ej: Google News)
    """
    title: str
    link: str
    published: datetime
    summary: str
    source: str = "Google News RSS"
    
    def to_dict(self):
        """Convierte el resultado a diccionario."""
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published.isoformat() if isinstance(self.published, datetime) else self.published,
            "summary": self.summary,
            "source": self.source
        }
    
    def __repr__(self) -> str:
        return (f"WebSearchResult(title={self.title[:50]}..., "
                f"source={self.source})")
