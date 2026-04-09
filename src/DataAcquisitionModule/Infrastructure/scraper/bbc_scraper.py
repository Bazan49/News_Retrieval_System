from bs4 import BeautifulSoup
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
import json
from datetime import datetime
import re

class BBCScraper(BaseScraper):
    
    """Scraper específico para BBC, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_date(self, article, soup=None):
        """
        Extrae la fecha de publicación de un artículo BBC.
        Devuelve un objeto datetime o None si no se encuentra.
        """
        soup = soup or BeautifulSoup(article.html, "html.parser")
        script = soup.find("script", type="application/ld+json")
        if not script or not script.string:
            return None

        try:
            data = json.loads(script.string)
            # Tomar el primer elemento de @graph
            item = data.get("@graph", [{}])[0]
            date_str = item.get("datePublished")

            if not date_str:
                return None

            # Convertir ISO 8601 a datetime
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        except (json.JSONDecodeError, TypeError, IndexError, ValueError):
            return None
        
    def extract_authors(self, article, soup=None):
        """
        Extrae los autores de un artículo BBC.
        """

        soup = soup or BeautifulSoup(article.html, "html.parser")
        script = soup.find("script", type="application/ld+json")
        if not script or not script.string:
            return []

        try:
            data = json.loads(script.string)
            # Tomar el primer elemento de @graph
            item = data.get("@graph", [{}])[0]
            author_data = item.get("author")

            if not author_data:
                return []

            # Convertir a lista
            if isinstance(author_data, dict):
                return [author_data.get("name")] if "name" in author_data else []
            elif isinstance(author_data, list):
                return [a.get("name") for a in author_data if "name" in a]
        except (json.JSONDecodeError, TypeError, IndexError):
            return []

    def extract_content(self, article, soup=None):

        """Extrae el contenido principal de un artículo BBC, incluyendo texto de párrafos y subtítulos, 
        pero excluyendo enlaces y texto irrelevante."""

        soup = soup or BeautifulSoup(article.html, "html.parser")

        # Contenedor principal del artículo
        article_divs = soup.select("div.css-1k9op6x.e17x9cvu0")

        content = []

        for div in article_divs:
            # Iterar sobre todos los hijos directos del div en orden
            for elem in div.children:
                # Ignorar elementos que no sean tags
                if not hasattr(elem, "name"):
                    continue

                # Párrafos <p> sin enlaces
                if elem.name == "p" and not elem.find("a"):
                    text = elem.get_text(separator=" ", strip=True)
                    # Ignorar texto específico que no aporta al contenido
                    if text == "Y recuerda que puedes recibir notificaciones en nuestra app. Descarga la última versión y actívalas.":
                        continue
                    if text:
                        text = re.sub(r'\s+', ' ', text).strip()
                        content.append(text)

                # Subtítulos <h2>
                elif elem.name == "h2":
                    text = elem.get_text(separator=" ", strip=True)
                    if text:
                        text = re.sub(r'\s+', ' ', text).strip()
                        content.append(text)

        # Unir todo en un texto limpio
        article_text = "\n\n".join(content)
        
        return self.clean_text(article_text)