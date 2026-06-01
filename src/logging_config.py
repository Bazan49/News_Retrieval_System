import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("app.log", encoding="utf-8")]
    )
    # Silenciar logs de Elasticsearch (solo mostrar warnings o superiores)
    logging.getLogger("elastic_transport").setLevel(logging.WARNING)
    logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)
    logging.getLogger("elastic_transport.node_pool").setLevel(logging.WARNING)
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)