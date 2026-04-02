from urllib.parse import urlparse
from DataAcquisitionModule.Infrastructure.scraper.actualidad_rt_scraper import ActualidadRTScraper
from DataAcquisitionModule.Infrastructure.scraper.bbc_scraper import BBCScraper
from DataAcquisitionModule.Infrastructure.scraper.cubadebate_scraper import CubadebateScraper
from DataAcquisitionModule.Infrastructure.scraper.base_scraper import BaseScraper
from DataAcquisitionModule.Infrastructure.scraper.presidencia_scraper import PresidenciaScraper
from DataAcquisitionModule.Infrastructure.scraper.telemundo_scraper import TeleMundoScraper
from DataAcquisitionModule.Infrastructure.scraper.telesur_scraper import TeleSurScraper

class ScraperFactory:

    @staticmethod
    def get_scraper(url):
        # Extraer el dominio
        source = urlparse(url).netloc.lower()  # ej: 'www.cubadebate.cu'

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
        }

        # Devolver scraper adecuado o BaseScraper por defecto
        return scrapers.get(source, BaseScraper)()