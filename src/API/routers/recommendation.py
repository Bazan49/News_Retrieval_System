from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from src.API.schemas.recommendation_request import RecommendationRequestSchema
from src.API.dependencies import get_recommender
from src.API.schemas.recommendation_response import RecommendationResponse
from src.API.mappers.recommendation_mapper import map_to_recommendation_response
from src.RecommendationModule.Domain.entities import RecommendationRequest
from src.RecommendationModule.Application.content_based_recommender import ContentRecommender

router = APIRouter(prefix="/recommend", tags=["recommendation"])

@router.get("/for-user", response_model=RecommendationResponse)
async def recommend_for_user(
    req: RecommendationRequestSchema = Depends(),   # Toma todos los parámetros de consulta
    recommender: ContentRecommender = Depends(get_recommender)
):
    # El token tiene prioridad sobre el user_id enviado en la query
    final_user_id = req.user_id
    if not final_user_id:
        raise HTTPException(status_code=400, detail="User ID required (via token or query parameter)")

    # Crear el objeto de dominio
    request = RecommendationRequest(
        user_id=final_user_id,
        max_results=req.max_results,
        include_likes=req.include_likes,
        include_queries=req.include_queries,
        query_weight=req.query_weight
    )

    result = await recommender.recommend(request)
    return map_to_recommendation_response(result.user_id, result.recommended_docs)