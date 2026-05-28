from pydantic import BaseModel, Field
from typing import Optional

class RecommendationRequestSchema(BaseModel):
    user_id: str = Field(..., description="ID del usuario (obligatorio si no hay token)")
    max_results: int = Field(10, ge=1, le=50, description="Número máximo de recomendaciones")
    include_likes: bool = Field(True, description="Incluir likes en el perfil")
    include_queries: bool = Field(True, description="Incluir consultas recientes")
    query_weight: float = Field(0.3, ge=0, le=1, description="Peso de las consultas (0-1)")