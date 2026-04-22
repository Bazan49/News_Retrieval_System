from src.DataAcquisitionModule.Infrastructure.network.fetcher import Fetcher
from src.DataAcquisitionModule.Infrastructure.crawler.robots_policies import RobotsManager
from src.DataAcquisitionModule.Infrastructure.crawler.frontier_manager import FrontierManager
from src.DataAcquisitionModule.Infrastructure.crawler.url_filter import URLFilter
import time

class Crawler:

    def __init__(self, max_depth=3, delay = 1):
        self.max_depth = max_depth
        self.delay = delay
        self.frontier = FrontierManager()
        self.url_filter = URLFilter()

    def crawl(self, max_pages=50):

        pages_crawled = 0

        while self.frontier.frontier_list and pages_crawled < max_pages:

            url, depth = self.frontier.get_next_url()

            if not url:
                break

            if url in self.frontier.visited:
                continue

            # Verificar robots.txt antes de descargar
            if not RobotsManager.can_fetch(url, user_agent="MiCrawler/1.0"):
                self.frontier.add_to_visited(url)
                continue

            html = Fetcher.fetch(url)

            if not html:
                continue

            # Retornar url, html
            yield url, html

            links = Fetcher.extract_links(html, url)

            # Limitar profundidad
            if depth < self.max_depth:

                for link in links:

                    if not self.frontier.already_seen(link):

                        if self.url_filter.is_valid_url(link):

                            self.frontier.add_to_frontier(link,depth + 1)

            self.frontier.add_to_visited(url)

            # Guardar archivos
            self.frontier.save_frontier()
            self.frontier.save_visited()

            pages_crawled += 1

            time.sleep(self.delay)

