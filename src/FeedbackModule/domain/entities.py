from attr import dataclass
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class Feedback(BaseModel):
    query: str
    chunk_id: str
    chunk_content: str   # opcional, pero útil para refinar después
    rating: bool         # True = 👍, False = 👎
    user_id: Optional[str] = None
    timestamp: datetime = datetime.now()

@dataclass
class RefinementResult:
    original_query: str
    expanded_query: str
    results: Optional[List[HybridSearchResult]]