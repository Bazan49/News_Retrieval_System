import re
import unicodedata
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from newspaper import Article
from src.DataAcquisitionModule.Domain.Entities import scrapedDocument
from src.DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from src.DataAcquisitionModule.Domain.Interfaces.scraper import IScraper

class BaseScraper(IScraper):

    """Clase base para scrapers, utilizando Newspaper3k para extracción de contenido"""
    """Neswpapr3k es una librería robusta que maneja la mayoría de los casos de scraping, 
    pero esta clase puede ser extendida para casos específicos."""

    def extract(self, url, html) -> scrapedDocument:

        source = self.get_source(url)
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
    
    def clean_text(self, text):
        if not text:
            return ""
        
        # Normalizar unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Eliminar caracteres de control (excepto saltos y tabs)
        text = ''.join(
            c for c in text 
            if unicodedata.category(c) != 'Cc' or c in '\n\t'  
        )
        
        # Normalizar saltos de línea
        text = re.sub(r'\r\n?', '\n', text)         
        
        # Limpiar espacios múltiples
        text = re.sub(r'[\t ]+', ' ', text)  

        # Limpiar espacios alrededor de saltos de línea
        text = re.sub(r' *\n *', '\n', text)       
        
        # Reducir saltos excesivos (mantener párrafos)
        text = re.sub(r'\n{3,}', '\n\n', text)      
        
        return text.strip()

    def extract_title(self, article, soup=None):
        return article.title

    def extract_content(self, article, soup=None):
        return self.clean_text(article.text)

    def extract_authors(self, article, soup=None):
        return article.authors
    
    def extract_date(self, article, soup=None):
        return article.publish_date

