from typing import Any, Dict, List
from WebSearchModule.Domain.insufficiency_detector import InsufficientResultsDetector


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
        min_results: int = 3,
        min_score_threshold: float = -50.0,
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
        self.min_score_threshold = min_score_threshold
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
        retrieved_results: List[Dict[str, Any]]
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
        
        # Score por cantidad de resultados
        if num_results < self.min_results:
            quantity_score = (self.min_results - num_results) / self.min_results
        else:
            quantity_score = 0.0
        
        # Score por puntuación promedio
        scores = [
            result.get("score", 0.0)
            for result in retrieved_results
            if "score" in result
        ]
        
        quality_score = 0.0
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score < self.min_score_threshold:
                # Normalizar: qué tan lejos del threshold
                difference = self.min_score_threshold - avg_score
                quality_score = min(1.0, difference / 100.0)
        
        # Combinar scores: 60% cantidad, 40% calidad
        insufficiency = (0.6 * quantity_score) + (0.4 * quality_score)
        return min(1.0, max(0.0, insufficiency))
