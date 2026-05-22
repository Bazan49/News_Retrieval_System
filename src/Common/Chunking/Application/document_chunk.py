from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

# Metadata fuertemente tipada para un chunk de noticia
@dataclass
class ChunkMetadata:
    doc_id: str
    source: str
    title: str
    publication_date: Optional[datetime] = None
    authors: Optional[list] = None          # Lista de autores
    chunk_number: int = 0
    estimated_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "doc_id": self.doc_id,
            "source": self.source,
            "title": self.title,
            "authors": self.authors if self.authors else ["Unknown"],
            "chunk_number": self.chunk_number,
            "estimated_tokens": self.estimated_tokens,
        }
        # Solo agregar publication_date si existe 
        if self.publication_date:
            result["publication_date"] = self.publication_date.isoformat()
        return result

@dataclass
class Chunk:
    """Unidad de chunk procesada."""
    chunk_id: str
    content: str
    metadata: ChunkMetadata
