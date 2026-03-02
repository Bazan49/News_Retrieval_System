from bs4 import BeautifulSoup
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from newspaper import Article

class Scraper:

    def __init__(self):
        pass

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
    
    def is_invalid_title(self, title, source_name):

        """Determina si el título es incorrecto (vacío o igual al nombre del medio)"""

        if not title:
            return True
        
        title = title.strip().lower()
        
        # Si el título es igual al nombre del medio
        if title == source_name.lower():
            return True
        
        return False
    
    def extract_title(self, article, source):

        """
        Extrae el título del artículo usando múltiples estrategias
        """

        title = article.title

        if not self.is_invalid_title(title, source):
            return self.clean_text(title)

        soup = BeautifulSoup(article.html, "html.parser")

        # 🔹 Intentar Open Graph
        meta_og = soup.find("meta", property="og:title")
        if meta_og and meta_og.get("content"):
            return self.clean_text(meta_og["content"])

        # 🔹 Intentar H1
        h1 = soup.find("h1")
        if h1:
            return self.clean_text(h1.get_text())

        # 🔹 Intentar etiqueta <title>
        html_title = soup.find("title")
        if html_title:
            return self.clean_text(html_title.get_text())

        # 3️⃣ Si todo falla
        return "Título no encontrado"

    def process_url(self, url, source=None, discovered_at=None):

        try:

            url_normalized = self.normalize_url(url)

            article = Article(url, language="es")
            article.download()
            article.parse()

            title = self.extract_title(article, source)
            content = article.text
            authors = article.authors
            publish_date = article.publish_date
            html = article.html
            # images = article.images
            
            content_clean = self.clean_text(content) 

            # content_hash = self.generate_hash(content_clean)

            document_data = {
                "source": source,
                "url": url,
                "url_normalized": url_normalized,
                "title": title,
                "content": content_clean,
                "authors": authors,
                "date": publish_date,
                # "html": html
                # "images": images,
                # "content_hash": content_hash,
                "scraped_at": datetime.now(timezone.utc),
                "discovered_at": discovered_at,
                "indexed": False,
                "embeddings_generated": False
            }

            print(title)
        
        except Exception as e:
            print(f"Error procesando {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = Scraper()
    # Ejemplo de uso
    url = "http://www.cubadebate.cu/noticias/2026/03/02/presidente-cubano-convoca-a-implementar-transformaciones-necesarias-al-modelo-economico-y-social/"
    result = scraper.process_url(url, "cubadebate")
