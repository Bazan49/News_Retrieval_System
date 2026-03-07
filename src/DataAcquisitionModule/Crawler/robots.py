from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time

# Cache para no descargar robots.txt cada vez
_parsers = {}

def can_fetch(url: str, user_agent: str = "*") -> bool:
    """
    Devuelve True si el user-agent puede acceder a la URL según robots.txt.
    Descarga robots.txt una sola vez por dominio.
    """
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    
    if domain not in _parsers:
        robots_url = f"{domain}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception as e:
            print(f"Error al leer robots.txt de {domain}: {e}")
            # Ante error, permitir por defecto
            _parsers[domain] = None
            return True
        _parsers[domain] = rp
    
    rp = _parsers[domain]
    if rp is None:
        return True  # No se pudo obtener, permitir
    
    return rp.can_fetch(user_agent, url)