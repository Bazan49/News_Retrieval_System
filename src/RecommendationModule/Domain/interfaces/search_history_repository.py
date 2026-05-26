from abc import ABC, abstractmethod
from typing import List

class SearchHistoryRepository(ABC):
    @abstractmethod
    async def save_query(self, user_id: str, query: str) -> None:
        pass

    @abstractmethod
    async def get_recent_queries(self, user_id: str, limit: int = 20) -> List[str]:
        pass