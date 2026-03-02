"""
frontier.py

Módulo encargado de manejar:

- frontier.csv
- visited.csv

Responsabilidades:

- Cargar frontier
- Guardar frontier
- Cargar visited
- Guardar visited
- Obtener siguiente URL
- Agregar nuevas URLs
"""
import os



class FrontierManager:

    def __init__(self):

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.FRONTIER_FILE = os.path.join(BASE_DIR, "frontier.csv")
        self.VISITED_FILE = os.path.join(BASE_DIR, "visited.csv")
        self.SEEDS_FILE = os.path.join(BASE_DIR, "seeds.csv")

        # Estructuras en memoria
        self.frontier_list, self.frontier_set = self.load_frontier()
        self.visited = self.load_visited()


    # SEEDS

    def load_seeds(self):

        try:
            with open(self.SEEDS_FILE, "r", encoding="utf-8") as f:

                return [
                    line.strip()
                    for line in f
                    if line.strip()
                ]

        except FileNotFoundError:
            return []


    # FRONTIER

    def load_frontier(self):

        try:
            with open(self.FRONTIER_FILE, "r", encoding="utf-8") as f:

                urls = [
                    line.strip()
                    for line in f
                    if line.strip()
                ]

        except FileNotFoundError:
            urls = []

        # Si frontier vacío → usar seeds
        if not urls:
            urls = self.load_seeds()

        frontier_list = [(url, 0) for url in urls]
        frontier_set = set(urls)

        return frontier_list, frontier_set


    def save_frontier(self):

        with open(self.FRONTIER_FILE, "w", encoding="utf-8") as f:

            for url, depth in self.frontier_list:
                f.write(url + "\n")


    def add_to_frontier(self, url, depth):

        if url not in self.frontier_set:

            self.frontier_list.append((url, depth))
            self.frontier_set.add(url)


    def get_next_url(self):

        if self.frontier_list:

            url, depth = self.frontier_list.pop(0)

            self.frontier_set.remove(url)

            return url, depth

        return None, None


    # VISITED

    def load_visited(self):

        try:
            with open(self.VISITED_FILE, "r", encoding="utf-8") as f:

                return set(
                    line.strip()
                    for line in f
                    if line.strip()
                )

        except FileNotFoundError:
            return set()


    def save_visited(self):

        with open(self.VISITED_FILE, "w", encoding="utf-8") as f:

            for url in self.visited:
                f.write(url + "\n")


    def add_to_visited(self, url):

        self.visited.add(url)


    def already_seen(self, url):

        if url in self.frontier_set:
            return True

        if url in self.visited:
            return True

        return False