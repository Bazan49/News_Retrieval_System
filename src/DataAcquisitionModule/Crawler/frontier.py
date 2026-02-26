"""
frontier.py

Módulo encargado de manejar:

- frontier.txt (URLs pendientes de visitar)
- visited.txt (URLs ya visitadas)

Responsabilidades:
- Cargar frontier
- Guardar frontier
- Cargar visited
- Guardar visited
- Obtener siguiente URL
- Agregar nuevas URLs
"""

FRONTIER_FILE = "frontier.txt"
VISITED_FILE = "visited.txt"

# FRONTIER

def load_frontier():
    """
    Carga las URLs pendientes desde frontier.txt
    """

    try:
        with open(FRONTIER_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    except FileNotFoundError:
        return []


def save_frontier(frontier):
    """
    Guarda la lista de URLs pendientes
    """

    with open(FRONTIER_FILE, "w", encoding="utf-8") as f:

        for url in frontier:
            f.write(url + "\n")


def add_to_frontier(frontier, url):
    """
    Agrega una URL a frontier si no existe
    """

    if url not in frontier:
        frontier.append(url)


def get_next_url(frontier):
    """
    Obtiene la siguiente URL del frontier
    """

    if frontier:
        return frontier.pop(0)

    return None


# VISITED

def load_visited():
    """
    Carga las URLs visitadas
    """

    try:
        with open(VISITED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())

    except FileNotFoundError:
        return set()


def save_visited(visited):
    """
    Guarda las URLs visitadas
    """

    with open(VISITED_FILE, "w", encoding="utf-8") as f:

        for url in visited:
            f.write(url + "\n")


def add_to_visited(visited, url):
    """
    Marca una URL como visitada
    """

    visited.add(url)


# UTILIDADES

def already_seen(url, frontier, visited):
    """
    Verifica si una URL ya fue vista
    """

    if url in frontier:
        return True

    if url in visited:
        return True

    return False