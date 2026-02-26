"""
url_filter.py

Módulo encargado de validar URLs.

Responsabilidades:

- Permitir solo URLs del dominio seleccionado
- Evitar archivos no HTML (pdf, jpg, etc.)
- Filtrar URLs inválidas
"""

from urllib.parse import urlparse

# Cambiar el dominio
DOMAIN = "bbc.com"


# Extensiones no descargar
BLOCKED_EXTENSIONS = [

    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".zip",
    ".rar",
    ".mp4",
    ".mp3",
    ".css",
    ".js"

]


# VALIDACIÓN DE URL

def is_valid_url(url):
    """
    Verifica si una URL es válida para el crawler.
    """

    try:

        parsed = urlparse(url)

        # http o https
        if parsed.scheme not in ["http", "https"]:
            return False

        # pertenecer al dominio
        if DOMAIN not in parsed.netloc:
            return False

        # Evitar archivos no HTML
        for ext in BLOCKED_EXTENSIONS:

            if parsed.path.lower().endswith(ext):
                return False

        return True

    except:

        return False