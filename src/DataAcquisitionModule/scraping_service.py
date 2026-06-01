import asyncio
from typing import Optional
from src.DataAcquisitionModule.scraper.scraper_factory import ScraperFactory
from src.DataAcquisitionModule.network.fetcher import Fetcher
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument
import logging

logger = logging.getLogger("DataAcquisitionModule.ScrapingService")

class ScrapingService:
    async def scrape_url(self, url: str) -> Optional[ScrapedDocument]:
        
        try:
            # 1. Descargar HTML
            html = await asyncio.to_thread(Fetcher.fetch, url)
            if not html:
                return None

            # 2. Obtener scraper
            scraper = ScraperFactory.get_scraper(url)

            # 3. Extraer documento
            document = await asyncio.to_thread(scraper.extract, url, html)
            if not document:
                return None
            
            logger.info("Documento extraído correctamente | url=%s, título=%s", url, document.title[:50])
            return document
        except Exception as e:
            logger.error("Error inesperado durante el scraping | url=%s, error=%s", url, str(e), exc_info=True)
            return None
        