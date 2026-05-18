from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class SearchDocument:
    """Documento limpio para indexación"""
    chunk_id: str
    url: str
    source: str
    title: str
    content: str
    authors: Optional[List[str]]
    date: Optional[datetime]
    chunk_number: str

