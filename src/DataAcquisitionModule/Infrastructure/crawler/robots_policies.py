import gzip
import io
from urllib.request import urlopen, Request
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time

class RobotsManager:
    _parsers = {}
    TTL_SECONDS = 3600

    @classmethod
    def _fetch_robots_txt(cls, robots_url):
        """Descarga robots.txt y devuelve el texto decodificado, manejando gzip."""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',  # Indicamos que aceptamos compresión
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        req = Request(robots_url, headers=headers)
        
        with urlopen(req, timeout=10) as response:
            content_encoding = response.headers.get("Content-Encoding", "")
            raw_data = response.read()
            
            if "gzip" in content_encoding:
                with gzip.GzipFile(fileobj=io.BytesIO(raw_data)) as gz:
                    text = gz.read().decode("utf-8")
            elif "deflate" in content_encoding:
                import zlib
                try:
                    text = zlib.decompress(raw_data, -zlib.MAX_WBITS).decode("utf-8")
                except zlib.error:
                    text = raw_data.decode("utf-8")
            else:
                text = raw_data.decode("utf-8")
            return text

    @classmethod
    def can_fetch(cls, url: str, user_agent: str = "*") -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print(f"[RobotsManager] URL inválida o sin dominio: {url} -> Permitiendo acceso por seguridad")
            return True
        
        domain = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{domain}/robots.txt"

        # ---- Caché ----
        if domain in cls._parsers:
            parser, timestamp = cls._parsers[domain]
            if time.time() - timestamp < cls.TTL_SECONDS:
                if parser is None:
                    print(f"[RobotsManager] Cache: robots.txt de {domain} no disponible (error previo) -> Permitiendo acceso por defecto")
                    return True
                else:
                    allowed = parser.can_fetch(user_agent, url)
                    print(f"[RobotsManager] Cache: {user_agent} puede acceder a {url} según robots.txt de {domain}: {allowed}")
                    return allowed
            else:
                # Caché expirada, la eliminamos para volver a descargar
                del cls._parsers[domain]
                print(f"[RobotsManager] Caché expirada para {domain}, se volverá a descargar robots.txt")

        # ---- Descarga fresh ----
        try:
            print(f"[RobotsManager] Descargando robots.txt desde {robots_url} ...")
            content = cls._fetch_robots_txt(robots_url)
            
            print("===== robots.txt de", domain, "=====")
            print(content)
            print("================================")
    
            rp = RobotFileParser()
            rp.parse(content.splitlines())
            cls._parsers[domain] = (rp, time.time())
            allowed = rp.can_fetch(user_agent, url)
            print(f"[RobotsManager] {user_agent} puede acceder a {url} según robots.txt recién descargado: {allowed}")
            return allowed
        except Exception as e:
            print(f"[RobotsManager] ERROR al leer robots.txt de {domain}: {e}")
            print(f"[RobotsManager] -> Permitiendo acceso por defecto (fallback seguro)")
            cls._parsers[domain] = (None, time.time())
            return True