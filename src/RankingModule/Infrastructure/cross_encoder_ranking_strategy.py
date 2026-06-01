from typing import List, Optional
import asyncio
from sentence_transformers import CrossEncoder
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.RankingModule.Domain.Interfaces.ranking_strategy import RankingStrategy

import logging
logger = logging.getLogger("RankingModule.CrossEncoderRankingStrategy") 

class CrossEncoderRankingStrategy(RankingStrategy):
    def __init__(self, cross_encoder_model: CrossEncoder):
        self.cross_encoder_model = cross_encoder_model
    
    async def rerank(self, results: List[HybridSearchResult], query: Optional[str]) -> List[HybridSearchResult]:
        if not query or not results:
            return results

        logger.info("Aplicando re‑ranking con cross‑encoder | entrada=%d", len(results))

        pairs = [(query, f"{r.title}\n\n{r.content}") for r in results]
        scores = await asyncio.to_thread(self.cross_encoder_model.predict, pairs)

        for result, score in zip(results, scores):
            result.cross_encoder_score = float(score)

        # Reordenar por cross_encoder_score descendente
        results.sort(key=lambda x: x.cross_encoder_score, reverse=True)
        
        return results