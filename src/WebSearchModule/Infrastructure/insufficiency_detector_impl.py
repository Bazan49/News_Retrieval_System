from typing import Any, Dict, List
from src.WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector
from src.RetrievalModule.Domain.retrieval_result import RetrievalResult

class SimpleInsufficientResultsDetector(InsufficientResultsDetector):
    """
    Detector simple de insuficiencia basado en cantidad y puntuación de resultados.
    
    Criterios:
    - Pocos resultados (< min_results)
    - Puntuaciones bajas (promedio < min_score_threshold)
    - Falta de resultados = insuficiente
    """
    
    def __init__(
        self, 
        min_results: int = 15,
        empty_results_insufficient: bool = True
    ):
        """
        Inicializa el detector de insuficiencia.
        
        Args:
            min_results: Número mínimo de resultados considerado suficiente
            min_score_threshold: Puntuación mínima promedio aceptable
            empty_results_insufficient: Si True, sin resultados = insuficiente
        """
        self.min_results = min_results
        self.empty_results_insufficient = empty_results_insufficient
    
    async def is_insufficient(
        self, 
        query: str, 
        retrieved_results: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> bool:
        """
        Determina si los resultados son insuficientes.
        
        Args:
            query: Consulta (informativa, no se usa en la lógica)
            retrieved_results: Resultados recuperados
            threshold: Umbral de insuficiencia (0-1)
            
        Returns:
            True si insuficiente, False si suficiente
        """
        score = await self.get_insufficiency_score(query, retrieved_results)
        return score > threshold
    
    async def get_insufficiency_score(
        self,
        query: str,
        retrieved_results: List[RetrievalResult]
    ) -> float:
        """
        Calcula score de insuficiencia (0-1).
        
        Args:
            query: Consulta
            retrieved_results: Resultados recuperados
            
        Returns:
            Score donde 0 = suficiente, 1 = muy insuficiente
        """
        # Sin resultados = máxima insuficiencia
        if not retrieved_results:
            return 1.0 if self.empty_results_insufficient else 0.0
        
        num_results = len(retrieved_results)
        
        if num_results < self.min_results:
            return 1.0  
        else:
            return 0.0