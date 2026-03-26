from sympy import re
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper

class TeleMundoScraper(BaseScraper):
    
    """Scraper específico para TeleMundo, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_authors(self, article):

        """Extrae los autores de artículos de TeleMundo buscando patrones comunes en el texto"""

        inicio = article.text[:300]  # solo el inicio del artículo

        match = re.search(r"^Por ([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ, y]+)", inicio)

        if not match:
            return article.authors

        authors = match.group(1)

        authors = authors.replace(" y ", ", ")
        authors_list = [a.strip() for a in authors.split(",")]

        return authors_list
