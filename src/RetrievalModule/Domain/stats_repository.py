from abc import ABC, abstractmethod
from typing import Dict, Counter

class StatsRepository(ABC):
    @abstractmethod
    async def get_doc_term_freqs(self) -> Dict[str, Counter]:
        """Retorna {doc_id: Counter({term: tf})}"""
        pass

    @abstractmethod
    async def get_doc_lengths(self) -> Dict[str, int]:
        """Retorna {doc_id: length}"""
        pass

    @abstractmethod
    async def get_collection_freq(self) -> Counter:
        """Retorna Counter({term: freq})"""
        pass