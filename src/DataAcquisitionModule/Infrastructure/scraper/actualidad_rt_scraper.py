from bs4 import BeautifulSoup
from src.DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
import json
from datetime import datetime
import re

class ActualidadRTScraper(BaseScraper):

    """Scraper específico para Actualidad RT, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_content(self, article, soup=None) -> str:
        """
        Extrae contenido principal de artículos RT:
        - Párrafos principales
        - Títulos h2/h3
        - Listas de items
        - Citas
        Ignora ruido (scripts, links, ads, tweets).
        """
        soup = soup or BeautifulSoup(article.html, 'html.parser')

        container = soup.select_one('div.ArticleView-text')  
        if not container:
            return self.clean_text(article.text)
        
        # Elimina elementos no deseados dentro del contenedor
        for twitter in container.find_all('div', class_='EmbedBlock-twitter'):
            twitter.decompose()

        # Selectores específicos para RT + genéricos
        selectors = [
            'div.Text-root > p',      # Párrafos principales de RT
            'h2',                   # Subtítulos de nivel 2
            'h3',                   # Subtítulos de nivel 3
            'li',                   # Items de listas
            'blockquote',           # Citas
        ]
        
        texts = []
        
        for elem in container.select(', '.join(selectors)):
            
            text = elem.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)  # Normaliza espacios
            
            if(text):
                texts.append(text)

        # Elimina "MINUTO A MINUTO" al final del contenido si está presente
        if texts:
            texts[-1] = re.sub(
                r'[,;:.\-]?\s*MINUTO A MINUTO.*',
                '',
                texts[-1],
                flags=re.IGNORECASE
            ).strip()
            if not texts[-1]:
                texts.pop()
                
        content = '\n\n'.join(texts)
        return self.clean_text(content) 

    def extract_date(self, article, soup=None):
        if not soup:
            soup = BeautifulSoup(article.html, "html.parser")

        # -------- 1. JSON-LD --------
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            if not script.string:
                continue

            try:
                data = json.loads(script.string)

                if data.get("@type") in ["Article", "NewsArticle"]:
                    date_str = data.get("datePublished")

                    if date_str:
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            except:
                continue

        # -------- 2. META fallback --------
        meta_date = soup.find("meta", {"name": "publish-date"})
        if meta_date and meta_date.get("content"):
            try:
                return datetime.fromisoformat(meta_date.get("content"))
            except:
                pass

        return None
        
    def extract_authors(self, article, soup=None):
        if not soup:
            soup = BeautifulSoup(article.html, "html.parser")

        # -------- 1. JSON-LD --------
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            if not script.string:
                continue

            try:
                data = json.loads(script.string)

                if data.get("@type") in ["Article", "NewsArticle"]:
                    author = data.get("author")

                    if isinstance(author, dict):
                        return [author.get("name")] if author.get("name") else []

                    elif isinstance(author, list):
                        return [a.get("name") for a in author if a.get("name")]

            except:
                continue

        # -------- 2. META fallback --------
        meta_author = soup.find("meta", {"property": "article:author"})
        if meta_author and meta_author.get("content"):
            return [meta_author.get("content")]

        return []