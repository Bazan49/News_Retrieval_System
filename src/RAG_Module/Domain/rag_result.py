from dataclasses import dataclass
from typing import List
from src.Common.RetrievalResult.retrieval_result import RetrievalResult

@dataclass
class RAGResult:
    query: str
    answer: str
    sources: List[RetrievalResult]  