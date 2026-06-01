import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger("DataAcquisitionModule.Fetcher")

class Fetcher:
    """Módulo encargado de descargar páginas web y extraer enlaces."""

    @staticmethod
    def fetch(url, max_retries=3):
        """
        Descarga una página web.
        Devuelve el HTML o None si falla.
        """

        for attempt in range(1, max_retries + 1):

            try:
                logger.info(f"Downloading ({attempt}/{max_retries}): {url}")

                response = requests.get(url, timeout=8)

                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response.text

                logger.error(f"Status error: {response.status_code}")

            except requests.exceptions.Timeout:
                logger.error(f"Timeout: {url}")

            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error: {url}")

            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")

            if attempt < max_retries:
                logger.info("Reintentando...")
                time.sleep(2)

        logger.error(f"Fallo al descargar después de {max_retries} intentos: {url}")
        return None

    @staticmethod
    def extract_links(html, base_url):

        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):

            link = urljoin(base_url, a["href"])

            if link.startswith("http"):
                links.add(link)

        return list(links)
