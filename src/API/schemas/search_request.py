from pydantic import BaseModel, Field
from typing import Literal

class SearchQueryParams(BaseModel):
    q: str = Field(..., description="Texto de búsqueda", min_length=1)
    k: int = Field(10, description="Número de resultados", ge=1, le=50)