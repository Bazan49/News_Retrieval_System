import gzip
import io
import time
import zlib
from urllib.request import urlopen, Request
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from urllib.error import URLError
import chardet

class RobotsManager:
    _parsers = {}
    TTL_SECONDS = 3600
    REQUEST_TIMEOUT = 30      
    MAX_RETRIES = 2           # reintentos adicionales
    RETRY_DELAY = 2           # segundos base entre reintentos

    @classmethod
    def _decode_response(cls, raw_data: bytes) -> str:
        """Decodifica bytes a str usando primero UTF-8, luego chardet, y por último latin-1."""
        # Intento rápido con UTF-8
        try:
            return raw_data.decode("utf-8")
        except UnicodeDecodeError:
            pass

        # Detección automática con chardet
        detected = chardet.detect(raw_data)
        encoding = detected.get("encoding")
        confidence = detected.get("confidence", 0)

        if encoding and confidence > 0.5:
            try:
                return raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                pass

        # Fallback final: latin-1
        return raw_data.decode("latin-1")

    @classmethod
    def _fetch_robots_txt(cls, robots_url: str, retry: int = 0) -> str:
        """Descarga robots.txt manejando compresión gzip/deflate y decodificación robusta."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        req = Request(robots_url, headers=headers)

        try:
            with urlopen(req, timeout=cls.REQUEST_TIMEOUT) as response:
                content_encoding = response.headers.get("Content-Encoding", "")
                raw_data = response.read()

                # Descompresión
                if "gzip" in content_encoding:
                    with gzip.GzipFile(fileobj=io.BytesIO(raw_data)) as gz:
                        data = gz.read()
                elif "deflate" in content_encoding:
                    try:
                        data = zlib.decompress(raw_data, -zlib.MAX_WBITS)
                    except zlib.error:
                        data = raw_data
                else:
                    data = raw_data

                # Decodificación robusta
                text = cls._decode_response(data)
                return text

        except (URLError, TimeoutError, Exception) as e:
            if retry < cls.MAX_RETRIES:
                wait = cls.RETRY_DELAY * (retry + 1)
                print(f"[RobotsManager] Error en {robots_url} (intento {retry+1}/{cls.MAX_RETRIES+1}): {e}. Reintentando en {wait}s...")
                time.sleep(wait)
                return cls._fetch_robots_txt(robots_url, retry + 1)
            else:
                # Re-lanzar después de reintentos fallidos
                raise

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