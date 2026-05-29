from pydantic import BaseModel
from typing import Optional, List
from src.API.schemas.hybrid_response import HybridSearchResultSchema

class FeedbackRequest(BaseModel):
    query: str
    chunk_id: str
    chunk_content: str
    rating: bool
    user_id: Optional[str] = None

class RefineRequest(BaseModel):
    original_query: str
    chunk_content: Optional[str] = None
    chunk_contents: Optional[List[str]] = None

    def get_contents(self) -> List[str]:
        if self.chunk_contents:
            return self.chunk_contents
        if self.chunk_content:
            return [self.chunk_content]
        return []

class RefineResponse(BaseModel):
    original_query: str
    expanded_query: str
    results: List[HybridSearchResultSchema]