"""
crawler.py

Módulo principal del crawler.

Responsabilidades:

- Descargar páginas web
- Extraer enlaces
- Filtrar URLs válidas
- Actualizar frontier
- Actualizar visited
"""

import requests
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin

MAX_DEPTH = 3 

from frontier import FrontierManager

from url_filter import URLFilter

from robots import can_fetch


# CONFIGURACION

class Crawler:
    def __init__(self, max_depth=3, delay=1):
        """
        Constructor del crawler
        """

        self.MAX_DEPTH = max_depth
        self.DELAY = delay

        # Instanciar el manejador de frontier (URLs pendientes / visitadas)
        self.frontier = FrontierManager()

        # Instanciar el filtro de URLs
        self.url_filter = URLFilter()


        # Cargar estructuras
        # self.frontier.frontier_list, self.frontier_set = self.frontier.load_frontier()
        # self.visited = self.frontier.load_visited()

        print("Crawler iniciado")
        print("Frontier:", len(self.frontier.frontier_set))
        print("Visited:", len(self.frontier.visited))



    def fetch(self, url, max_retries=3):
        """
        Descarga una página web.
        Devuelve el HTML o None si falla.
        """

        for attempt in range(1, max_retries + 1):

            try:
                print(f"\nDownloading ({attempt}/{max_retries}): {url}")

                response = requests.get(url, timeout=8)

                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response.text

                print("Status error:", response.status_code)

            except requests.exceptions.Timeout:
                print("Timeout:", url)

            except requests.exceptions.ConnectionError:
                print("Connection error:", url)

            except Exception as e:
                print("Error downloading:", url, e)

            if attempt < max_retries:
                print("Reintentando...")
                time.sleep(2)

        print("Fallo al descargar después de", max_retries, "intentos:", url)
        return None



    def extract_links(self, html, base_url):

        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):

            link = urljoin(base_url, a["href"])

            if link.startswith("http"):
                links.add(link)

        return list(links)



    def crawl(self, max_pages=50):

        pages_crawled = 0

        while self.frontier.frontier_list and pages_crawled < max_pages:

            url, depth = self.frontier.get_next_url()

            if not url:
                break

            # Verificar robots.txt antes de descargar
            if not can_fetch(url, user_agent="MiCrawler/1.0"):   
                print(f"Bloqueado por robots.txt: {url}")
                self.frontier.add_to_visited(url)   
                continue
        
            if url in self.frontier.visited:
                continue

            html = self.fetch(url)

            if not html:
                continue

            print(f"Crawling: {url} | Profundidad: {depth}")

            links = self.extract_links(html, url)

            print("Links encontrados:", len(links))

            # Limitar profundidad
            if depth < self.MAX_DEPTH:

                for link in links:

                    if not self.frontier.already_seen(link):

                        if self.url_filter.is_valid_url(link):

                            self.frontier.add_to_frontier(link,depth + 1)

            self.frontier.add_to_visited(url)

            # Guardar archivos
            self.frontier.save_frontier()
            self.frontier.save_visited()

            pages_crawled += 1

            print("Paginas crawleadas:", pages_crawled)
            print("Tamano del frontier:", len(self.frontier.frontier_set))

            time.sleep(self.DELAY)

        print("\nCrawler terminado")