from pydantic import BaseModel
from typing import List
from src.API.schemas.search_response import SearchResultItem

class RAGResponseSchema(BaseModel):
    query: str
    answer: str
    sources: List[SearchResultItem]