from pydantic import BaseModel
from typing import List, Optional
from src.API.schemas.search_response import SearchResultItem

class RecommendationResponse(BaseModel):
    user_id: str
    recommended_docs: List[SearchResultItem]
    scores: List[float]