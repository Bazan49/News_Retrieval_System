from bs4 import BeautifulSoup
from src.DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper

class CubadebateScraper(BaseScraper):

    """Scraper específico para Cubadebate, extiende BaseScraper para manejar casos particulares de este sitio"""

    def extract_title(self, article, soup=None):

        """Extrae el título de artículos de Cubadebate """

        soup = soup or BeautifulSoup(article.html, "html.parser")

        meta_og = soup.find("meta", property="og:title")
        if meta_og and meta_og.get("content"):
            return self.clean_text(meta_og["content"])

        # Si falla o no lo encuentra, retornar título extraído por newspaper
        return article.title

    def extract_authors(self, article, soup=None):

        """Extrae los autores de artículos de Cubadebate """

        soup = soup or BeautifulSoup(article.html, "html.parser")

        if(article.authors):
            return article.authors

        soup = BeautifulSoup(article.html, "html.parser")

        authors = []

        for strong in soup.find_all("strong"):
            if "Por" in strong.text:
                parent = strong.parent
                links = parent.find_all("a")

                for a in links:
                    authors.append(a.get_text(strip=True))
                
                break

        return authors