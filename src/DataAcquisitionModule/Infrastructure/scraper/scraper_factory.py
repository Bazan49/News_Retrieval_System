from urllib.parse import urlparse
from cubadebate_scraper import CubadebateScraper
from base_scraper import BaseScraper
from telemundo_scraper import TeleMundoScraper

class ScraperFactory:

    def get_scraper(self, url):
        # Extraer el dominio
        source = urlparse(url).netloc.lower()  # ej: 'www.cubadebate.cu'

        # Diccionario de mapping source → scraper
        scrapers = {
            "cubadebate.cu": CubadebateScraper,
            "www.cubadebate.cu": CubadebateScraper,  
            "telemundo.com": TeleMundoScraper,
            "www.telemundo.com": TeleMundoScraper
        }

        # Devolver scraper adecuado o BaseScraper por defecto
        return scrapers.get(source, BaseScraper)()