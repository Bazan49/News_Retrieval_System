from abc import ABC, abstractmethod
from typing import Any, Dict, List


class InsufficientResultsDetector(ABC):
    """
    Interfaz para determinar si los resultados de búsqueda locales 
    son insuficientes para responder una consulta.
    """
    
    @abstractmethod
    async def is_insufficient(
        self, 
        query: str, 
        retrieved_results: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> bool:
        """
        Determina si los resultados recuperados son insuficientes.
        
        Args:
            query: Consulta del usuario
            retrieved_results: Resultados recuperados del índice local
            threshold: Umbral de relevancia/cobertura (0-1)
            
        Returns:
            True si se considera insuficiente, False si hay suficiente información
        """
        pass
    
    @abstractmethod
    async def get_insufficiency_score(
        self,
        query: str,
        retrieved_results: List[Dict[str, Any]]
    ) -> float:
        """
        Calcula un score que indica qué tan insuficientes son los resultados (0-1).
        
        Returns:
            Score donde 0 = suficiente, 1 = muy insuficiente
        """
        pass
