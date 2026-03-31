from bs4 import BeautifulSoup
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
import json
from datetime import datetime

class ActualidadRTScraper(BaseScraper):

    """Scraper específico para Actualidad RT, extiende BaseScraper para manejar casos particulares de este sitio"""

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