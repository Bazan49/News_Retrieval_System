from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from src.AuthModule.Application.dependencies import get_current_user_optional
from src.API.schemas.feedback import FeedbackRequest, RefineRequest, RefineResponse
from src.API.mappers.feedback_mapper import map_refinement_result_to_response
from src.FeedbackModule.application.feedback_service import FeedbackService
from src.FeedbackModule.application.refinement_service import RefinementService
from src.API.dependencies import get_feedback_service, get_refinement_service, get_hybrid_service

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/")
async def add_feedback(req: FeedbackRequest, current_user: Optional[str] = Depends(get_current_user_optional), service: FeedbackService = Depends(get_feedback_service)):
    user_id = current_user or req.user_id
    try:
        await service.add_feedback(query=req.query, chunk_id=req.chunk_id, chunk_content=req.chunk_content, rating=req.rating, user_id=user_id)
        return {"status": "success", "message": "Feedback guardado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine", response_model=RefineResponse)
async def refine_search(
    req: RefineRequest,
    refinement_service: RefinementService = Depends(get_refinement_service),
    search_service = Depends(get_hybrid_service)
):
    refinement_result = await refinement_service.refine_search(
        original_query=req.original_query,
        chunk_contents=req.get_contents(),
        search_service=search_service
    )
    return map_refinement_result_to_response(refinement_result)