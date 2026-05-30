import asyncio
from typing import Optional
from src.DataAcquisitionModule.scraper.scraper_factory import ScraperFactory
from src.DataAcquisitionModule.network.fetcher import Fetcher
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument

class ScrapingService:
    async def scrape_url(self, url: str) -> Optional[ScrapedDocument]:
        
        print(f"🔍 Scraping URL: {url}")
        try:
            # 1. Descargar HTML
            html = await asyncio.to_thread(Fetcher.fetch, url)
            if not html:
                print(f"❌ No se pudo descargar la página: {url}")
                return None
            
            print(f"✅ Descargados {len(html)} caracteres HTML")

            # 2. Obtener scraper
            scraper = ScraperFactory.get_scraper(url)
            print(f"📦 Scraper utilizado: {scraper.__class__.__name__}")

            # 3. Extraer documento
            document = await asyncio.to_thread(scraper.extract, url, html)
            if not document:
                print(f"❌ El scraper no pudo extraer el documento")
                return None
            
            print(f"✅ Documento extraído: {document.title[:50]}...")
            return document
        except Exception as e:
            print(f"❌ Error inesperado scraping {url}: {e}")
            return None
        