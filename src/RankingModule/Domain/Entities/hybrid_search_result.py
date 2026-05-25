from dataclasses import dataclass
from typing import Optional, List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from enum import Enum

class ResultSource(Enum):
    LOCAL = "local"   # proviene de búsqueda local (sparse/dense)
    WEB = "web"       # proviene de expansión web

@dataclass
class HybridSearchResult:
    retrieval_result: RetrievalResult
    rrf_score: float
    final_score: Optional[float] = None
    sparse_score: Optional[float] = None
    dense_score: Optional[float] = None
    sparse_rank: Optional[int] = None   
    dense_rank: Optional[int] = None   
    source_type: ResultSource = ResultSource.LOCAL   # origen del resultado

    # Delegación de propiedades para acceso directo
    @property
    def doc_id(self) -> str:
        return self.retrieval_result.doc_id

    @property
    def url(self) -> str:
        return self.retrieval_result.url

    @property
    def title(self) -> str:
        return self.retrieval_result.title

    @property
    def content(self) -> str:
        return self.retrieval_result.content

    @property
    def date(self) -> Optional[str]:
        return self.retrieval_result.date

    @property
    def source(self) -> str:
        return self.retrieval_result.source

    @property
    def authors(self) -> Optional[List[str]]:
        return self.retrieval_result.authors
    