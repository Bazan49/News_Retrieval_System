from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class RetrievalResult:
    """Representa un resultado de búsqueda recuperado"""
    
    doc_id: str               # identificador único del chunk (ej. "url_0")
    url: str                  # URL base del documento padre
    title: str
    content: str              # texto del chunk
    score: float
    source: str
    snippet: Optional[str] = None
    authors: Optional[List[str]] = None   
    date: Optional[str] = None
    chunk_number: Optional[int] = None   
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "snippet": self.snippet,
            "authors": self.authors,
            "date": self.date,
            "chunk_number": self.chunk_number
        }