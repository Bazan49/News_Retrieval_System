from pydantic import BaseModel
from typing import List
from src.API.schemas.hybrid_response import HybridSearchResultSchema

class RAGResponseSchema(BaseModel):
    query: str
    answer: str
    sources: List[HybridSearchResultSchema]