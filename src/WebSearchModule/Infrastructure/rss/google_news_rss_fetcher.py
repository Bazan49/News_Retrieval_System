import feedparser
import urllib.parse
import asyncio
from datetime import datetime
from typing import List
from WebSearchModule.Domain.web_search_result import WebSearchResult
from WebSearchModule.Domain.web_search_repository import WebSearchRepository


class GoogleNewsRSSFetcher(WebSearchRepository):
    """
    Implementación de búsqueda web usando Google News RSS.
    Permite buscar noticias recientes sobre cualquier tema.
    """
    
    def __init__(self, lang: str = "es-419", country: str = "US"):
        """
        Inicializa el fetcher de Google News RSS.
        
        Args:
            lang: Código de idioma (ej: es-419 para español latino)
            country: Código de país (ej: US, ES, MX)
        """
        self.lang = lang
        self.country = country
        self.base_url = "https://news.google.com/rss/search"
    
    async def search(self, query: str, max_results: int = 10) -> List[WebSearchResult]:
        """
        Busca noticias en Google News RSS de forma asincrónica.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados (por defecto 10)
            
        Returns:
            Lista de WebSearchResult con los artículos encontrados
        """
        try:
            # Ejecutar la búsqueda en un thread pool para no bloquear
            results = await asyncio.to_thread(
                self._fetch_rss_sync,
                query,
                max_results
            )
            return results
        except Exception as e:
            print(f"Error fetching Google News RSS: {e}")
            return []
    
    def _fetch_rss_sync(self, query: str, max_results: int) -> List[WebSearchResult]:
        """
        Realiza la búsqueda sincrónica en Google News RSS.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de WebSearchResult
        """
        # Construir URL con parámetros
        q = urllib.parse.quote_plus(query)
        ceid = f"{self.country}:es"
        rss_url = (
            f"{self.base_url}?"
            f"q={q}&hl={self.lang}&gl={self.country}&ceid={ceid}"
        )
        
        # Parsear feed RSS
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            return []
        
        results = []
        for entry in feed.entries[:max_results]:
            try:
                # Parsear fecha de publicación
                published = self._parse_date(entry.get("published", ""))
                
                # Crear resultado
                result = WebSearchResult(
                    title=entry.get("title", ""),
                    link=entry.get("link", ""),
                    published=published,
                    summary=entry.get("summary", ""),
                    source="Google News RSS"
                )
                results.append(result)
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue
        
        return results
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """
        Parsea fecha en formato RFC 2822 (usado por Google News RSS).
        
        Args:
            date_str: String de fecha
            
        Returns:
            objeto datetime
        """
        if not date_str:
            return datetime.now()
        
        try:
            # Intenta parsear formato común de RSS
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            try:
                # Intenta otros formatos comunes
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except Exception:
                return datetime.now()
