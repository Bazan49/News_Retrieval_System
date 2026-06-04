import requests
import time
from requests.exceptions import Timeout, ConnectionError
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("DataAcquisitionModule.Fetcher")

class Fetcher:
    @staticmethod
    def fetch(url, max_retries=3):
        """Descarga una página web. Reintenta solo para errores transitorios."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Downloading ({attempt}/{max_retries}): {url}")
                response = requests.get(url, timeout=8)

                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response.text

                # Si el código de estado es 4xx (error del cliente), no reintentar.
                if 400 <= response.status_code < 500:
                    logger.error(f"Client error {response.status_code} (no retry): {url}")
                    return None

                # Para otros códigos (5xx, etc.) reintentar (hasta max_retries)
                logger.error(f"Server error {response.status_code}, will retry...")
                # No retornar aún, se reintentará

            except Timeout:
                logger.error(f"Timeout: {url}")
            except ConnectionError:
                logger.error(f"Connection error: {url}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

            # Si llegamos aquí (error transitorio o código 5xx), esperamos y reintentamos
            if attempt < max_retries:
                logger.info("Reintentando...")
                time.sleep(2)

        logger.error(f"Failed after {max_retries} attempts: {url}")
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
