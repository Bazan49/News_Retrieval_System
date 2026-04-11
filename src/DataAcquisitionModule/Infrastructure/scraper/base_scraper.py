import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from newspaper import Article
from DataAcquisitionModule.Domain.Entities import scrapedDocument
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from DataAcquisitionModule.Domain.Interfaces.scraper import IScraper

class BaseScraper(IScraper):

    """Clase base para scrapers, utilizando Newspaper3k para extracción de contenido"""
    """Neswpapr3k es una librería robusta que maneja la mayoría de los casos de scraping, 
    pero esta clase puede ser extendida para casos específicos."""

    def extract(self, url, html) -> scrapedDocument:

        url_normalized = self.normalize_url(url)
        source = self.get_source(url_normalized)
        article = self.build_article(url, html)

        # Validar que sea un artículo real (no una página de categoría, por ejemplo)
        soup = BeautifulSoup(article.html, "html.parser")
        og_type = soup.find('meta', {'property': 'og:type'})
        if og_type and og_type.get('content') != 'article':
            return None

        # Extraer contenido y validar longitud mínima
        content = self.extract_content(article, soup)
        if not content or len(content.strip()) < 500:
            return None

        document = ScrapedDocument(
                source=source,
                url=url,
                url_normalized=url_normalized,
                title=self.extract_title(article, soup),
                content=content,
                authors=self.extract_authors(article, soup),
                date=self.extract_date(article, soup),
            )
        
        return document

    def build_article(self, url, html):
        article = Article(url, language="es")
        if not html:
            article.download()
        else:
            article.set_html(html)
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
        # 1. Normaliza saltos de línea (por si hay \r\n o múltiples \n)
        text = re.sub(r'\r\n?', '\n', text)
        
        # 2. Reemplaza múltiples espacios dentro de una línea por uno solo
        lines = text.split('\n')
        cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in lines]
        
        # 3. Une las líneas, conservando saltos de línea solo si no están vacías
        return '\n'.join([line for line in cleaned_lines if line])

    def extract_title(self, article, soup=None):
        return article.title

    def extract_content(self, article, soup=None):
        return self.clean_text(article.text)

    def extract_authors(self, article, soup=None):
        return article.authors
    
    def extract_date(self, article, soup=None):
        return article.publish_date

