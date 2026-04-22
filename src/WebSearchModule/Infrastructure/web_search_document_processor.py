from datetime import datetime
from typing import List
import hashlib
from src.WebSearchModule.Domain.web_search_result import WebSearchResult
from src.IndexModule.Domain.search_document import SearchDocument

class WebSearchDocumentProcessor:
    """
    Convierte resultados de búsqueda web en SearchDocument listos para indexar.
    Similar a DefaultDocumentProcessor pero para resultados de web search.
    """
    
    def process_web_result(self, web_result: WebSearchResult) -> SearchDocument:
        """
        Convierte un WebSearchResult en SearchDocument.
        
        Args:
            web_result: Resultado de búsqueda web
            
        Returns:
            SearchDocument listo para indexar
        """
        return SearchDocument(
            source=web_result.source,
            url=web_result.link,
            title=web_result.title,
            content=web_result.summary,
            authors=None,  # No disponible en RSS
            date=web_result.published if isinstance(web_result.published, datetime) 
                 else datetime.fromisoformat(web_result.published)
        )
    
    def process_batch(self, web_results: List[WebSearchResult]) -> List[SearchDocument]:
        """
        Convierte un lote de WebSearchResult en SearchDocument.
        
        Args:
            web_results: Lista de resultados de búsqueda web
            
        Returns:
            Lista de SearchDocument
        """
        return [self.process_web_result(result) for result in web_results]
    
    def generate_short_id(self, url: str) -> str:
        """
        Genera un ID corto único para documentos web basado en hash de la URL.
        
        Args:
            url: URL del documento
            
        Returns:
            ID corto único (máximo 32 caracteres)
        """
        # Usar hash SHA256 y tomar primeros 16 caracteres
        hash_obj = hashlib.sha256(url.encode('utf-8'))
        short_id = hash_obj.hexdigest()[:16]
        return f"web_{short_id}"
