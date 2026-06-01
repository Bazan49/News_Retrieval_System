from typing import Callable, List, Optional
from src.RankingModule.Domain.Interfaces.scoring_strategy import ScoringStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult, ResultSource

import logging
logger = logging.getLogger("RankingModule.RankingService") 

class RankingService:
    """
    Servicio que calcula la prioridad de visualización (posicionamiento) de cada resultado
    mediante una combinación lineal de:
    - relevancia (normalizada a partir de rrf_score o cross_encoder_score)
    - personalización (personalization_similarity)
    - frescura (recency_score)
    """
    def __init__(
        self,
        w_relevance: float,
        w_personalization: float,
        w_recency: float,
        scoring_strategies: List[ScoringStrategy],
        activate_cross_encoder: bool = True
    ):
        self.w_relevance = w_relevance
        self.w_personalization = w_personalization
        self.w_recency = w_recency
        self.strategies = scoring_strategies
        self.activate_cross_encoder = activate_cross_encoder

    async def compute(self, results: List[HybridSearchResult], user_id: Optional[str]) -> List[HybridSearchResult]:
        """
        Calcula final_score para cada resultado y ordena la lista de mayor a menor prioridad.
        """
        logger.info("Aplicando posicionamiento final de los resultados | entrada=%d", len(results))

        if not results:
            return results

        # Aplicar todas las estrategias de scoring (cada una asigna sus campos)
        for strategy in self.strategies:
            await strategy.apply(results, user_id=user_id)

        # Normalizar la fuente de relevancia elegida
        if self.activate_cross_encoder:
            self._min_max_normalize(results, score_fn=lambda r: r.cross_encoder_score or 0.0, default_value=0.5)
        else:
            self._min_max_normalize(results, score_fn=lambda r: r.rrf_score, default_value=0.5)

        # Calcular final_score
        for r in results:
            r.final_score = (
                self.w_relevance * r.relevance_score +
                self.w_personalization * (r.personalization_similarity or 0.0) +
                self.w_recency * (r.recency_factor or 0.0)
            )

        # Ordenar por final_score descendente
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results

    def _min_max_normalize(
        self,
        results: List[HybridSearchResult],
        score_fn: Callable[[HybridSearchResult], float],
        default_value: float = 0.5,
    ) -> None:
        """
        Aplica Min-Max normalization a un score extraído de HybridSearchResult
        y guarda el resultado en `HybridSearchResult.relevance_score`.
        """
        scores = [score_fn(r) for r in results]

        if not scores:
            for r in results:
                r.relevance_score = default_value
            return

        min_s = min(scores)
        max_s = max(scores)

        for r, score in zip(results, scores):
            if max_s > min_s:
                norm_score = (score - min_s) / (max_s - min_s)
            else:
                # Todos iguales
                norm_score = default_value 

            r.relevance_score = norm_score