from fastapi import APIRouter, Depends, HTTPException
from src.API.schemas.recommendation_request import RecommendationRequestSchema
from src.API.dependencies import get_recommender
from src.API.schemas.recommendation_response import RecommendationResponse
from src.API.mappers.recommendation_mapper import map_to_recommendation_response
from src.RecommendationModule.Domain.entities import RecommendationRequest
from src.RecommendationModule.Application.content_based_recommender import ContentRecommender

router = APIRouter(prefix="/recommend", tags=["recommendation"])

@router.post("/for-user", response_model=RecommendationResponse)
async def recommend_for_user(
    req: RecommendationRequestSchema, 
    recommender: ContentRecommender = Depends(get_recommender)
):
    try:
        result = await recommender.recommend(req)
        return map_to_recommendation_response(result.user_id, result.recommended_docs, result.scores)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))