import re
import json
from bs4 import BeautifulSoup
from src.DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
from datetime import datetime

class TeleMundoScraper(BaseScraper):
    
    """Scraper específico para TeleMundo, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_date(self, article, soup=None):

        """Extrae la fecha de publicación de artículos de TeleMundo buscando patrones comunes en el HTML"""

        if article.publish_date:
            return article.publish_date

        soup = soup or BeautifulSoup(article.html, 'html.parser')

        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            if not script.string:
                continue

            try:
                data = json.loads(script.string)

                if data.get("datePublished"):
                    date_str = data.get("datePublished")

                if date_str:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            except:
                continue
            
        return None

    def extract_authors(self, article, soup=None):

        """Extrae los autores de artículos de TeleMundo buscando patrones comunes en el texto"""

        inicio = article.text[:300]  # solo el inicio del artículo

        # Buscar patrones como "Por [nombre(s)]" al inicio del artículo
        match = re.search(r"^Por (.*?)(?:\s[-–—]\s|\n|$)", inicio) 

        if not match:
            return article.authors

        authors = match.group(1)

        authors = authors.replace(" y ", ", ")
        authors_list = [a.strip() for a in authors.split(",")]

        return authors_list
    
    def extract_content(self, article, soup) -> str:

        """
        Extrae el contenido principal de un artículo:
        - Párrafos con clase 'body-graf'
        - Títulos h2 
        - Items de listas 'li'
        - Títulos de pasos 'h3.body-heading'
        - Citas 'blockquote'
        Ignora banners, scripts y otros elementos irrelevantes como referencias externas
        y la línea de autor al inicio del texto"""
        
        soup = soup or BeautifulSoup(article.html, 'html.parser')

        container = soup.select_one('.article-body__content')

        selectors = [
            'p.body-graf',
            'li',
            'h2',
            'blockquote',
            'h3.body-heading'
        ]

        if not container:
            elements = []
        else:

            # Eliminar la sección de FAQ si existe, que suele estar al final del artículo 
            # y no es parte del contenido principal

            faq = container.select_one('div[data-testid="article-faq-embed"]')
            if faq:
                faq.decompose()
            
            # Buscar los elementos relevantes dentro del contenedor principal
            elements = container.select(', '.join(selectors))

        texts = []
        for elem in elements:

            # separator=' ' inserta espacios entre elementos inline
            text = elem.get_text(separator=' ', strip=True)
            # Normalizar espacios múltiples a uno solo
            text = re.sub(r'\s+', ' ', text)
            if text:
                texts.append(text)
                
        content = '\n\n'.join(texts) if texts else article.text

        # Eliminar la línea de autor al inicio del artículo si aparece, que suele empezar con "Por [nombre(s)]"
        content = re.sub(r"^Por .*\n", "", content, count=1)

        # Eliminar referencias externas entre corchetes
        content = re.sub(r"\[.*?\]", "", content)

        return self.clean_text(content)
    