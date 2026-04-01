import re
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper

class TeleMundoScraper(BaseScraper):
    
    """Scraper específico para TeleMundo, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_authors(self, article, soup=None):

        """Extrae los autores de artículos de TeleMundo buscando patrones comunes en el texto"""

        inicio = article.text[:300]  # solo el inicio del artículo

        # Buscar patrones como "Por [nombre(s)]" al inicio del artículo
        match = re.search(r"^Por (.*?)(?:\s[-–]\s|\n|$)", inicio) 

        if not match:
            return article.authors

        authors = match.group(1)

        authors = authors.replace(" y ", ", ")
        authors_list = [a.strip() for a in authors.split(",")]

        return authors_list
    
    def extract_content(self, article, soup=None):

        """Extrae el contenido del artículo de TeleMundo y realiza limpieza específica para este sitio, 
        como eliminar referencias externas y la línea de autor al inicio del texto"""

        content = article.text

        # Eliminar referencias externas entre corchetes
        content = re.sub(r"\[.*?\]", "", content)

        # Eliminar la línea de autor al inicio del artículo, que suele empezar con "Por [nombre(s)]"
        content = re.sub(r"^Por .*\n", "", content, count=1)

        return self.clean_text(content)
