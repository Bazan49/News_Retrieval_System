from abc import ABC, abstractmethod
from typing import List
from .retrieval_result import RetrievalResult


class Retriever(ABC):
    """
    Interfaz abstracta para modelo de recuperación.
    
    """
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        Recupera los documentos más relevantes para una consulta.
        
        Args:
            query: Consulta del usuario
            top_k: Número máximo de resultados a devolver
            
        Returns:
            Lista de RetrievalResult ordenados por relevancia descendente
        """
        pass
    
    @abstractmethod
    async def build_index(self) -> None:
        """
        Construye/actualiza el índice del modelo.
        
        Este método debe ser llamado antes de retrieve()
        si el índice no está construido o está desactualizado.
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> dict:
        """
        Retorna estadísticas del modelo (número de documentos, vocabulario, etc.)
        
        Returns:
            Diccionario con estadísticas del modelo
        """
        pass
