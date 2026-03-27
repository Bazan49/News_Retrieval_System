from DataAcquisitionModule.Infrastructure.crawler.crawler import Crawler
from DataAcquisitionModule.Infrastructure.scraper.scraper_factory import ScraperFactory
from DataAcquisitionModule.Infrastructure.storage.jsonl_storage_repository import JSONLRepository

class DataAcquisitionService:
    def __init__(self, max_pages=50, max_depth=3, delay=1):

        self.max_pages = max_pages
        self.crawler = Crawler(max_depth=max_depth, delay=delay)
        self.repository = JSONLRepository(path="data/initial_corpus.jsonl", batch_size=10)

    def run(self):

        for url, html in self.crawler.crawl(max_pages=self.max_pages):
            try:
                scraper = ScraperFactory.get_scraper(url)
                document = scraper.extract(url, html)
                self.repository.save(document)
                print(f"[OK] Document extracted and saved: {url}")
            except Exception as e:
                print(f"[ERROR] Failed to process {url}: {e}")

        self.repository.flush()
        print("Data acquisition finished.")