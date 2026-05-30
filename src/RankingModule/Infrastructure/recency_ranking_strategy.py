import math
from datetime import datetime, timezone
from dateutil import parser
from typing import List, Optional
from src.RankingModule.Domain.Interfaces.scoring_strategy import ScoringStrategy
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult

class RecencyScoringStrategy(ScoringStrategy):

    """
    Estrategia que calcula un factor de actualidad (recency_factor) para cada documento,
    basado en su fecha de publicación. El factor se calcula mediante decaimiento exponencial:

        recency = exp(-días_antigüedad / decay_days)

    donde `decay_days` es configurable (por defecto 30). 

    El factor se almacena en `result.recency_factor` (rango [0, 1]).
    """

    def __init__(
        self,
        recency_decay_days: int = 30,
    ):
        self.recency_decay_days = recency_decay_days

    async def apply(self, results: List[HybridSearchResult], user_id: Optional[str] = None):
        current_date = datetime.now(timezone.utc)

        for res in results:
            pub_date = res.date
            if not pub_date:
                res.recency_factor = 0.5
                continue

            try:
                pub_date = parser.parse(pub_date)
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                days_ago = (current_date - pub_date).days

                if days_ago < 0:
                    res.recency_factor = 1.0
                    continue

                # Score de recencia en (0, 1]: 1 hoy, decae exponencialmente con el tiempo
                recency_score = math.exp(-days_ago / self.recency_decay_days)
                res.recency_factor = recency_score

            except Exception as e:
                # Fallo en parsing → dato inválido
                print(f"Error parsing recency for doc {res.doc_id}: {pub_date} - Error: {e}")
                print(f"{current_date} {current_date.tzinfo} - {pub_date} {pub_date.tzinfo}")
                res.recency_factor = 0.5  # valor neutro para fechas inválidas
