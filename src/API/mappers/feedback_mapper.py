from src.API.schemas.feedback import RefineResponse
from src.API.mappers.hybrid_search_mapper import map_hybrid_to_schema
from ...FeedbackModule.domain.entities import RefinementResult

def map_refinement_result_to_response(result: RefinementResult) -> RefineResponse:
    return RefineResponse(
        original_query=result.original_query,
        expanded_query=result.expanded_query,
        results=[map_hybrid_to_schema(r) for r in result.results]
    )