import requests

class ProcessURL:

    def __init__(self, scraper):
        self.scraper = scraper

    def fetch_html(self, url):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def execute(self, url, html=None):

        try:
            
            if html is None:
                html = self.fetch_html(url)

            return self.scraper.extract(url, html)

        except Exception as e:
            print(f"Error procesando {url}: {e}")
            return None