from abc import ABC, abstractmethod
from src.DataAcquisitionModule.Domain.Entities import scrapedDocument

class IScraper(ABC):

    @abstractmethod
    def extract(self, url: str, html: str) -> scrapedDocument:
        pass