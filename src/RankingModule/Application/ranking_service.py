from typing import Callable, List, Optional
from src.RankingModule.Domain.Interfaces.scoring_strategy import ScoringStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

import logging
logger = logging.getLogger("RankingModule.RankingService")

class RankingService:
    """
    Servicio que calcula la prioridad de visualización (posicionamiento) de cada resultado
    mediante una combinación lineal de:
    - relevancia (normalizada a partir de rrf_score o cross_encoder_score)
    - personalización (personalization_similarity, normalizada dentro de la consulta)
    - frescura (recency_factor)
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
        logger.info("Aplicando posicionamiento final | entrada=%d", len(results))
        if not results:
            return results

        # Aplicar todas las estrategias de scoring (cada una asigna sus campos)
        for strategy in self.strategies:
            await strategy.apply(results, user_id=user_id)

        # Normalizar relevancia (rrf_score o cross_encoder_score) -> relevance_score
        if self.activate_cross_encoder:
            self._normalize_field(results, lambda r: r.cross_encoder_score or 0.0, "relevance_score", default_value=0.5)
        else:
            self._normalize_field(results, lambda r: r.rrf_score, "relevance_score", default_value=0.5)

        # Normalizar personalización -> personalization_similarity (sobrescribe el campo)
        self._normalize_field(results, lambda r: r.personalization_similarity or 0.0, "personalization_similarity", default_value=0.5)

        # Calcular final_score combinando los factores normalizados
        for r in results:
            r.final_score = (
                self.w_relevance * r.relevance_score +
                self.w_personalization * (r.personalization_similarity or 0.0) +
                self.w_recency * (r.recency_factor or 0.0)
            )

        results.sort(key=lambda x: x.final_score, reverse=True)
        return results

    def _normalize_field(
        self,
        results: List[HybridSearchResult],
        score_fn: Callable[[HybridSearchResult], float],
        target_attr: str,
        default_value: float = 0.5
    ) -> None:
        """
        Normaliza un campo numérico (extraído con score_fn) al rango [0,1] mediante min‑max
        y guarda el resultado en el atributo `target_attr` de cada resultado.
        Si todos los valores son iguales, asigna `default_value`.
        """
        scores = [score_fn(r) for r in results]
        if not scores:
            for r in results:
                setattr(r, target_attr, default_value)
            return

        min_s = min(scores)
        max_s = max(scores)
        if max_s > min_s:
            for r, score in zip(results, scores):
                norm = (score - min_s) / (max_s - min_s)
                setattr(r, target_attr, norm)
        else:
            for r, score in zip(results, scores):
                norm = default_value
                setattr(r, target_attr, norm)