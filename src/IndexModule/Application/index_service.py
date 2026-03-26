from typing import List
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from IndexModule.Domain.document_processor import DefaultDocumentProcessor
from IndexModule.Domain.index_repository import IndexRepository

class IndexService:
    def __init__(
        self,
        repository: IndexRepository,
        factory: DefaultDocumentProcessor
    ):
        self.repository = repository
        self.factory = factory
    
    async def index_scraped_documents(
        self, 
        scraped_docs: List['ScrapedDocument']
    ) -> None:
        """Orquesta indexación completa"""
        await self.repository.ensure_index()
        
        search_docs = [self.factory.process(doc) for doc in scraped_docs]
        await self.repository.index_bulk(search_docs)
        await self.repository.refresh()
