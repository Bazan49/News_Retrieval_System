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

from src.DataAcquisitionModule.Crawler.frontier import (
    load_frontier,
    save_frontier,
    load_visited,
    save_visited,
    get_next_url,
    add_to_frontier,
    add_to_visited,
    already_seen
)

from src.DataAcquisitionModule.Crawler.url_filter import is_valid_url

# CONFIGURACION
DELAY = 1   # segundos entre requests


# DESCARGA DE PAGINAS

def fetch(url):
    """
    Descarga una página web.
    Devuelve el HTML o None si falla.
    """

    try:

        print("\nDownloading:", url)

        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return response.text

        print("Status error:", response.status_code)

    except Exception as e:

        print("Error downloading:", url)

    return None


# EXTRACCION DE LINKS

def extract_links(html, base_url):
    """
    Extrae enlaces desde el HTML.
    Convierte URLs relativas a absolutas.
    """

    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):

        link = urljoin(base_url, a["href"])

        if link.startswith("http"):
            links.add(link)

    return list(links)



# CRAWLER PRINCIPAL

def crawl(max_pages=50):
    """
    Ejecuta el crawler.

    max_pages limita cuántas páginas visitar
    (evita crawls infinitos)
    """

    frontier = load_frontier()

    visited = load_visited()

    print("Crawler iniciado")
    print("Frontier:", len(frontier))
    print("Visited:", len(visited))

    pages_crawled = 0

    while frontier and pages_crawled < max_pages:

        url = get_next_url(frontier)

        if not url:
            break

        if url in visited:
            continue

        html = fetch(url)

        if not html:
            continue

        # Extraer enlaces
        links = extract_links(html, url)

        print("Links encontrados:", len(links))

        # Agregar nuevos links
        for link in links:

            if not already_seen(link, frontier, visited):

                if is_valid_url(link):

                    add_to_frontier(frontier, link)

        # Marcar visitado
        add_to_visited(visited, url)

        # Guardar archivos
        save_frontier(frontier)
        save_visited(visited)

        pages_crawled += 1

        print("Pages crawled:", pages_crawled)
        print("Frontier size:", len(frontier))

        time.sleep(DELAY)

    print("\nCrawler terminado")