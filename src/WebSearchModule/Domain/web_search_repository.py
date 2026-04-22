from abc import ABC, abstractmethod
from typing import List
from src.WebSearchModule.Domain.web_search_result import WebSearchResult


class WebSearchRepository(ABC):
    """Interfaz para obtener resultados de búsqueda web."""
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[WebSearchResult]:
        """
        Busca información en fuentes web (RSS).
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de WebSearchResult
        """
        pass
