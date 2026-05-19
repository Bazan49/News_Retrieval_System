from typing import List, Tuple
from src.Common.RetrievalResult.retrieval_result import RetrievalResult
from src.Common.Chunking.Application.document_chunk import Chunk
from src.RankingModule.Domain.Entities.hybrid_search_result import HybridSearchResult, ResultSource
from src.DataAcquisitionModule.scraping_service import ScrapingService
from googlenewsdecoder import new_decoderv1
import asyncio

class WebSearch:
    def __init__(self, web_search_repo, chunking_service, scraping_service=ScrapingService()):
        self.web_search_repo = web_search_repo
        self.chunking_service = chunking_service
        self.scraping_service = scraping_service

    async def fetch_web_results(self, query: str, max_results: int = 5) -> Tuple[List[HybridSearchResult], List[Chunk]]:
        raw_results = await self.web_search_repo.search(query, max_results=max_results)
        all_hybrids = []
        all_chunks = []
        semaphore = asyncio.Semaphore(5)  # máximo 5 tareas simultáneas

        async def process_one(raw):
            async with semaphore:
                real_url = self._clean_google_url(raw.link)
                doc = await self.scraping_service.scrape_url(real_url)
                if not doc:
                    return [], []
                chunks = self.chunking_service.chunk_document(doc)
                hybrids = []
                for chunk in chunks:
                    retrieval = RetrievalResult(
                        doc_id=chunk.chunk_id,
                        url=doc.url,
                        title=doc.title,
                        content=chunk.content,
                        score=0.0,
                        source=doc.source,
                        snippet=chunk.content[:200] + "...",
                        authors=doc.authors,
                        date=doc.date.isoformat() if doc.date else None,
                        chunk_number=chunk.metadata.chunk_number,
                        estimated_tokens=chunk.metadata.estimated_tokens
                    )
                    hybrid = HybridSearchResult(
                        retrieval_result=retrieval,
                        rrf_score=0.0,
                        source_type=ResultSource.WEB
                    )
                    hybrids.append(hybrid)
                return hybrids, chunks

        tasks = [process_one(raw) for raw in raw_results]
        results = await asyncio.gather(*tasks)

        for hybrids, chunks in results:
            all_hybrids.extend(hybrids)
            all_chunks.extend(chunks)

        return all_hybrids, all_chunks
    
    @staticmethod
    def _clean_google_url(url: str) -> str:
        if 'news.google.com' in url:
            try:
                decoded = new_decoderv1(url, interval=1)
                if decoded.get("status"):
                    return decoded["decoded_url"]
            except Exception as e:
                print(f"Error decoding Google News URL: {e}")
        return url