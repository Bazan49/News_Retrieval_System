from bs4 import BeautifulSoup
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from newspaper import Article
from scrapedDocument import ScrapedDocument 
import requests

class BaseScraper:

    def normalize_url(self, url):

        """Elimina parámetros y fragmentos para normalizar URL"""

        parsed = urlparse(url)
        clean = parsed._replace(query="", fragment="")
        return urlunparse(clean)

     
    def clean_text(self, text):

        """Limpia texto eliminando espacios extra y caracteres no deseados"""

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def generate_hash(self, content):

        """Genera un hash SHA-256 del contenido para detectar cambios"""

        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def fetch_html(self, url):

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def extract(self, url, html):

        article = Article(url, language="es")
        article.html = html
        article.parse()

        title = article.title
        content = article.text
        authors = article.authors
        date = article.publish_date

        return {
            "title": title,
            "content": content,
            "authors": authors,
            "date": date
        }

    def process_url(self, url, source=None, html=None):

        try:
            url_normalized = self.normalize_url(url)

            if html is None:
                html = self.fetch_html(url)

            extracted_data = self.extract(url, html)

            if not extracted_data:
                print("No se pudo extraer contenido")
                return None

            content_clean = self.clean_text(extracted_data["content"])
            # content_hash = self.generate_hash(content_clean)

            document = ScrapedDocument(
                source=source,
                url=url,
                url_normalized=url_normalized,
                title=extracted_data.get("title"),
                content=content_clean,
                authors=extracted_data.get("authors"),
                date=extracted_data.get("date"),
                # content_hash=content_hash,
                indexed=False,
                embeddings_generated=False
            )

            print(document.__dict__)

            return document
        
        except Exception as e:
            print(f"Error procesando {url}: {e}")
            return None
