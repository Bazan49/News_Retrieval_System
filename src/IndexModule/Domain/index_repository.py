from abc import ABC, abstractmethod
from typing import List, Optional
from .search_document import SearchDocument

class IndexRepository(ABC):
    """Interfaz pura para repositorios de indexación"""
    
    @abstractmethod
    async def index_one(self, doc: SearchDocument) -> None:
        pass
    
    @abstractmethod
    async def index_bulk(self, docs: List[SearchDocument]) -> None:
        pass
    
    @abstractmethod
    async def delete_by_id(self, doc_id: str) -> None:
        pass
    
    @abstractmethod
    async def ensure_index(self) -> None:
        pass
    
    @abstractmethod
    async def refresh(self) -> None:
        pass

    @abstractmethod
    async def get_term_frequency(
        self, 
        doc_id: str, 
        field: str, 
        term: str
    ) -> int:
        pass
