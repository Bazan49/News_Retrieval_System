"""
url_filter.py

Módulo encargado de validar URLs.
"""

from urllib.parse import urlparse

class URLFilter:

    def __init__(self):

        self.ALLOWED_DOMAINS = [

            "cubadebate.cu",
            "oncubanews.com",
            "bbc.com",
            "lanacion.com",
            "telesurtv.net",
            "actualidad.rt.com",
            "presidencia.gob.cu",
            "telemundo.com"

        ]

        self.BLOCKED_EXTENSIONS = [

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


    def is_valid_url(self, url):

        try:

            parsed = urlparse(url)

            # Solo http o https
            if parsed.scheme not in ["http", "https"]:
                return False


            # Verificar dominio permitido
            allowed = False

            for domain in self.ALLOWED_DOMAINS:

                if domain in parsed.netloc:
                    allowed = True
                    break

            if not allowed:
                return False


            # Verificar extensiones bloqueadas
            for ext in self.BLOCKED_EXTENSIONS:

                if parsed.path.lower().endswith(ext):
                    return False

            return True

        except:

            return False