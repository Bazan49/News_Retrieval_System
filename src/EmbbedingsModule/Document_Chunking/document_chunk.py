from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

# Metadata fuertemente tipada para un chunk de noticia
@dataclass
class ChunkMetadata:
    doc_id: str
    source: str
    url: str
    title: str
    publication_date: Optional[datetime] = None
    chunk_type: str = "paragraph"          # "paragraph", "subchunk", "title"
    chunk_number: int = 0
    estimated_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "publication_date": self.publication_date,
            "chunk_type": self.chunk_type,
            "chunk_number": self.chunk_number,
            "estimated_tokens": self.estimated_tokens,
        }

@dataclass
class Chunk:
    """Unidad de chunk procesada."""
    id: str
    content: str
    metadata: ChunkMetadata
