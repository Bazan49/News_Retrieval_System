from pydantic import BaseModel
class RecommendationRequestSchema(BaseModel):
    user_id: str
    max_results: int = 10
    include_likes: bool = True
    include_queries: bool = True
    query_weight: float = 0.3