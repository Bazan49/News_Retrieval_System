from abc import ABC, abstractmethod
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument

class IScraper(ABC):

    @abstractmethod
    def extract(self, url: str, html: str) -> ScrapedDocument:
        pass