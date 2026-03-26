from abc import ABC, abstractmethod
from DataAcquisitionModule.Domain.Entities import scrapedDocument

class Scraper(ABC):

    @abstractmethod
    def extract(self, url: str, html: str) -> scrapedDocument:
        pass