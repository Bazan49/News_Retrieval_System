import re
from baseScraper import BaseScraper
from newspaper import Article
import re

class TeleMundoScraper(BaseScraper):

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

    def extract(self, url, html):

        article = Article(url, language="es")
        article.html = html
        article.parse()

        title = article.title
        content = article.text
        authors = self.extract_authors(article)
        date = article.publish_date

        return {
            "title": title,
            "content": content,
            "authors": authors,
            "date": date
        }
    
    
