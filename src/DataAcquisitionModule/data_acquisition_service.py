import logging
from src.DataAcquisitionModule.crawler.crawler import Crawler
from src.DataAcquisitionModule.scraper.scraper_factory import ScraperFactory
from src.DataAcquisitionModule.storage.jsonl_storage_repository import JSONLRepository

logger = logging.getLogger("DataAcquisitionModule.DataAcquisitionService")
    
class DataAcquisitionService:
    def __init__(self, max_pages=50, max_depth=3, delay=1, batch_size=10, output_file="data/corpus.jsonl"):

        self.max_pages = max_pages
        self.crawler = Crawler(max_depth=max_depth, delay=delay)
        self.repository = JSONLRepository(path=output_file, batch_size=batch_size)

    def run(self):

        for url, html in self.crawler.crawl(max_pages=self.max_pages):
            try:
                scraper = ScraperFactory.get_scraper(url)
                document = scraper.extract(url, html)
                if document:
                    self.repository.save(document)
                    logger.info("Documento extraído y guardado | url=%s", url)
            except Exception as e:
                logger.error("Error al procesar URL | url=%s, error=%s", url, str(e), exc_info=True)

        self.repository.flush()
        logger.info("Adquisición finalizada")