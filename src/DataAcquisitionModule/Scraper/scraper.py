from anyio import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List
import csv
import os
from datetime import datetime

class Scraper:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "Data"
        self.csv_path = self.base_path / "scraped_pages.csv"  
        self.ensure_csv_exists()
    
    def scrape_page(self, html: str, url: str) -> dict:
       
        soup = BeautifulSoup(html, "html.parser")
        
        # Extraer datos
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        links = self._extract_internal_links(soup, url)
        
        result = {
            "url": url,
            "title": title,
            "text": text,
            "links": links
        }
        
        # Guardar automáticamente en CSV
        self._save_to_csv(result)
        
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> str:

        """Extrae título del <title> o primer <h1>"""

        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        return "" # página sin título detectable
    
    def _extract_text(self, soup: BeautifulSoup) -> List[str]:
        """Extrae todos los párrafos como lista"""
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(separator=" ", strip=True)
            if text and len(text) > 0:  
                paragraphs.append(text)
        return paragraphs
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Solo enlaces del mismo dominio"""
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Mismo dominio + HTTP/HTTPS
            if (parsed.netloc == base_domain and 
                parsed.scheme in ("http", "https")):
                
                # Normalizar (sin #fragment, sin / final duplicado)
                clean_url = full_url.split("#")[0].rstrip("/")
                links.add(clean_url)
        
        return sorted(list(links))

    def ensure_csv_exists(self):

        """Crea la carpeta data/ y el CSV con headers si no existe"""
        
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "url", "title", "text_count", "links_count"])

    def _save_to_csv(self, data: dict):
        """Guarda cada página scrapeada en el CSV principal"""
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                data["url"],
                data["title"][:200] + "..." if len(data["title"]) > 200 else data["title"],  # truncado
                len(data["text"]),
                len(data["links"])
            ])


def scrape_page(html: str, url: str) -> dict:
    
    scraper = Scraper()
    return scraper.scrape_page(html, url)

# Para uso directo (pruebas)
if __name__ == "__main__":
    # Ejemplo de uso
    html = "<html><title>Mi Título</title><p>Texto 1</p><p>Texto 2</p><a href='/pagina'>Link</a></html>"
    result = scrape_page(html, "https://ejemplo.com")
    print(result)
