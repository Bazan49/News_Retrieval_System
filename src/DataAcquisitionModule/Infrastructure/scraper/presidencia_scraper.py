from src.DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class PresidenciaScraper(BaseScraper):
    
    """Scraper específico para Presidencia, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_authors(self, article, soup=None):

        """Extrae los autores de artículos de Presidencia buscando patrones comunes en el texto"""

        if not soup:
            soup = BeautifulSoup(article.html, "html.parser")
        
        meta_author = soup.find("meta", {"property": "article:author"})
        if meta_author and meta_author.get("content"):
            authors_str = meta_author.get("content")
            authors = [author.strip() for author in authors_str.split('/')]
            return authors
    
        return [] 
        
    def extract_content(self, article, soup=None):

        """Extrae el contenido de artículos de Presidencia limpiando patrones repetitivos y no informativos"""
        
        content = article.text
        content = re.sub(r'Foto:.*?(?=\n|$)', '', content) # Eliminar información de foto
        return self.clean_text(content)