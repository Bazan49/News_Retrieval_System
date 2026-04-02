from datetime import datetime
import json
from bs4 import BeautifulSoup
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper

class TeleSurScraper(BaseScraper):

    """Scraper específico para teleSUR, extiende BaseScraper para manejar casos particulares de este sitio"""
    
    def extract_authors(self, article, soup=None):
        """
        Extrae los autores de un artículo de teleSUR usando:
        1️- JSON-LD si existe
        2- Etiqueta <p class="content-area__text__full__fuente__detalle"> que contiene "Autor:"
        """
        if not soup:
            soup = BeautifulSoup(article.html, "html.parser")

        authors = []

        # Buscar todos los scripts de tipo application/ld+json
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue

            # Puede ser un diccionario o lista
            if isinstance(data, dict):
                data_list = [data]
            elif isinstance(data, list):
                data_list = data
            else:
                continue

            # Buscar entradas con "author"
            for entry in data_list:
                if isinstance(entry, dict):
                    # Caso de BlogPosting o WebPage
                    author_info = entry.get("author")
                    if author_info:
                        if isinstance(author_info, list):
                            for a in author_info:
                                if isinstance(a, dict) and "name" in a:
                                    authors.append(a["name"])
                        elif isinstance(author_info, dict) and "name" in author_info:
                            authors.append(author_info["name"])

        # Si no se encontraron autores en JSON-LD, buscar en la etiqueta específica
        if not authors:
            p_autor = soup.find("p", class_="content-area__text__full__fuente__detalle", string=lambda s: s and s.strip().startswith("Autor:"))
            if p_autor:
                author = p_autor.get_text().replace("Autor:", "").strip()
                if author:
                    # Dividir por " y " o "," para manejar múltiples autores
                    authors = [a.strip() for a in author.replace(" y ", ",").split(",") if a.strip()]
            
        # Eliminar duplicados y vacíos (limpieza de seguridad)
        authors = list({a.strip() for a in authors if a}) 
        return authors
    
    def extract_date(self, article, soup=None):
        
        if(article.publish_date):
            return article.publish_date

        meta_updated = soup.find("meta", property="og:updated_time")
        if meta_updated and meta_updated.get("content"):
            date_str =  meta_updated["content"]
            # Convertir ISO 8601 a datetime
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        
        return None
    
    def extract_content(self, article, soup=None):

        content = article.text

        idx = content.find("\nAutor:")
        if idx != -1:
            content = content[:idx].strip()
        
        return self.clean_text(content)

            