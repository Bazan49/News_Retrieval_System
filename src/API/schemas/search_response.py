from pydantic import BaseModel
from typing import List, Optional

class SearchResultItem(BaseModel):
    id: str  
    title: str
    url: str
    source: str
    published_date: Optional[str] = None
    score: float
    snippet: str
    authors: Optional[List[str]] = None

class SearchResponseSchema(BaseModel):
    query: str
    results: List[SearchResultItem]

class RAGResponseSchema(BaseModel):
    query: str
    answer: str
    sources: List[SearchResultItem]