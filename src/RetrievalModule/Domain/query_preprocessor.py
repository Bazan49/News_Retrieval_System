from abc import ABC, abstractmethod
from typing import List

class QueryPreprocessor(ABC):
    @abstractmethod
    async def preprocess(self, text: str) -> List[str]:
        pass