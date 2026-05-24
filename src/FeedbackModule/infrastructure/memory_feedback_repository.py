from typing import List, Dict
from src.FeedbackModule.domain.entities import Feedback

class MemoryFeedbackRepository:
    def __init__(self):
        self._storage: List[Feedback] = []

    async def save(self, feedback: Feedback) -> None:
        self._storage.append(feedback)

    async def get_by_query_and_chunk(self, query: str, chunk_id: str) -> List[Feedback]:
        return [f for f in self._storage if f.query == query and f.chunk_id == chunk_id]

    async def get_all(self) -> List[Feedback]:
        return self._storage