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
    chunk_content: str

class RefineResponse(BaseModel):
    original_query: str
    expanded_query: str
    results: List[HybridSearchResultSchema]