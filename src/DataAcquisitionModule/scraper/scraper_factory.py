from urllib.parse import urlparse
from src.DataAcquisitionModule.scraper.specific_scrapers.actualidad_rt_scraper import ActualidadRTScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.bbc_scraper import BBCScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.cubadebate_scraper import CubadebateScraper
from src.DataAcquisitionModule.scraper.base_scraper import BaseScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.presidencia_scraper import PresidenciaScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.telemundo_scraper import TeleMundoScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.telesur_scraper import TeleSurScraper
from src.DataAcquisitionModule.scraper.specific_scrapers.la_nacion_scraper import LaNacionScraper

class ScraperFactory:

    @staticmethod
    def get_scraper(url):
        # Extraer el dominio
        source = urlparse(url).netloc.lower()  

        # Diccionario de mapping source → scraper
        scrapers = {
            "cubadebate.cu": CubadebateScraper,
            "www.cubadebate.cu": CubadebateScraper,  
            "telemundo.com": TeleMundoScraper,
            "www.telemundo.com": TeleMundoScraper,
            "www.bbc.com": BBCScraper,
            "bbc.com": BBCScraper,
            "actualidad.rt.com": ActualidadRTScraper,
            "www.actualidad.rt.com": ActualidadRTScraper,
            "presidencia.gob.cu": PresidenciaScraper,
            "www.presidencia.gob.cu": PresidenciaScraper,
            "telesurtv.net": TeleSurScraper,
            "www.telesurtv.net": TeleSurScraper,
            "lanacion.com.ar": LaNacionScraper,
            "www.lanacion.com.ar": LaNacionScraper
        }

        # Devolver scraper adecuado o BaseScraper por defecto
        return scrapers.get(source, BaseScraper)()