from baseScraper import BaseScraper
from bs4 import BeautifulSoup
from newspaper import Article

class CubadebateScraper(BaseScraper):

    def extract_authors(self, article):

        """Extrae los autores de artículos de Cubadebate """

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

    def extract_title(self, article):

        """Extrae el título de artículos de Cubadebate """

        soup = BeautifulSoup(article.html, "html.parser")

        meta_og = soup.find("meta", property="og:title")
        if meta_og and meta_og.get("content"):
            return self.clean_text(meta_og["content"])

        # Si falla o no lo encuentra, retornar título extraído por newspaper
        return article.title
    
    def extract(self, url, html):

        article = Article(url, language="es")
        article.html = html
        article.parse()

        title = self.extract_title(article)
        content = article.text
        authors = self.extract_authors(article)
        date = article.publish_date

        return {
            "title": title,
            "content": content,
            "authors": authors,
            "date": date
        }

