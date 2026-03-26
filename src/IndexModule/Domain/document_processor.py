from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from IndexModule.Domain.search_document import SearchDocument

class DefaultDocumentProcessor:
    """Procesador por defecto para ScrapedDocument -> SearchDocument"""
    
    def process(self, raw_doc: ScrapedDocument) -> SearchDocument:
        return SearchDocument(
            source=raw_doc.source,
            url=raw_doc.url,
            title=raw_doc.title or "",
            content=raw_doc.content or "",
            authors=raw_doc.authors or [],
            date=raw_doc.date
        )
    
