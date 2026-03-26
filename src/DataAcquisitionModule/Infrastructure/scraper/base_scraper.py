import re
from urllib.parse import urlparse, urlunparse
from newspaper import Article
from DataAcquisitionModule.Domain.Entities import scrapedDocument
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from DataAcquisitionModule.Domain.Interfaces.scraper import Scraper

class BaseScraper(Scraper):

    """Clase base para scrapers, utilizando Newspaper3k para extracción de contenido"""
    """Neswpapr3k es una librería robusta que maneja la mayoría de los casos de scraping, 
    pero esta clase puede ser extendida para casos específicos."""

    def extract(self, url, html) -> scrapedDocument:

        source = self.get_source(url_normalized)
        url_normalized = self.normalize_url(url)
        article = self.build_article(url, html)

        document = ScrapedDocument(
                source=source,
                url=url,
                url_normalized=url_normalized,
                title=self.extract_title(article),
                content=self.extract_content(article),
                authors=self.extract_authors(article),
                date=self.extract_date(article),
            )
        
        return document

    def build_article(self, url, html):
        article = Article(url, language="es")
        article.html = html
        article.parse()
        return article
    
    def get_source(self, url):
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    
    def normalize_url(self, url):
        parsed = urlparse(url)
        clean = parsed._replace(query="", fragment="")
        return urlunparse(clean)
    
    def clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_title(self, article):
        return article.title

    def extract_content(self, article):
        return self.clean_text(article.text)

    def extract_authors(self, article):
        return article.authors
    
    def extract_date(self, article):
        return article.publish_date

