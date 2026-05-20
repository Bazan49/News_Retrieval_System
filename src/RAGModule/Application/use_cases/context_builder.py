from typing import List
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult
from src.RAGModule.Domain.rag_context_item import RAGContextItem

class ContextBuilder:
    def __init__(self, max_chunks: int = 10, max_chunks_per_doc: int = 2):
        self.max_chunks = max_chunks
        self.max_chunks_per_doc = max_chunks_per_doc

    def build(self, hybrid_results: List[HybridSearchResult]) -> str:
        items = []
        doc_counts = {}

        for hr in hybrid_results:
            if len(items) >= self.max_chunks:
                break

            ret = hr.retrieval_result
            doc_id = ret.url

            # Límite por documento
            if doc_counts.get(doc_id, 0) >= self.max_chunks_per_doc:
                continue

            item = RAGContextItem(
                index=len(items) + 1,
                title=ret.title,
                text=ret.content,
                source=ret.source,
                date=ret.date
            )
            items.append(item)
            doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1

        context_str = self.format_for_prompt(items)
        return context_str

    def format_for_prompt(self, items: List[RAGContextItem]) -> str:
        parts = []
        for item in items:
            header = f"[{item.index}]"
            if item.source:
                header += f"\nsource: {item.source}"
            if item.date:
                header += f"\ndate: {item.date}"
            header += f"\ntitle: {item.title}"
            header += f"\ntext: {item.text}"
            parts.append(header)
        return "\n\n".join(parts)