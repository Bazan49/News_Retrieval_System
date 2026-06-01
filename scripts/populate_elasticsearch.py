import argparse
import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

# Asegurar que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar logging
from src.logging_config import setup_logging
setup_logging()
logger = logging.getLogger("PopulateElasticsearch")

from src.DI.config_container import ConfigContainer
from src.DI.disperse_search_container import SearchContainer
from src.DI.chunking_container import ChunkingContainer
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument

def parse_args():
    parser = argparse.ArgumentParser(description="Poblar ElasticSearch a partir de un archivo JSONL")
    parser.add_argument("--input-file", type=str, default="data/initial_corpus.jsonl",
                        help="Ruta al archivo JSONL de entrada (por defecto: data/initial_corpus.jsonl)")
    return parser.parse_args()

# Contenedores
_config_container = ConfigContainer()
_search_container = SearchContainer()
_chunking_container = ChunkingContainer()

_search_container.override_providers(
    settings=_config_container.settings,
)

_chunking_container.override_providers(
    settings=_config_container.settings,
)

# Servicios
chunking_service = _chunking_container.chunking_service()
index_service = _search_container.index_service()

async def main():
    args = parse_args()
    jsonl_path = Path(args.input_file)

    if not jsonl_path.exists():
        logger.error(f"Archivo no encontrado: {jsonl_path}")
        return

    scraped_docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Error JSON en línea {line_num}: {e}")
                continue

            pub_date = data.get("published_date")
            if pub_date:
                try:
                    date_obj = datetime.fromisoformat(pub_date)
                except ValueError:
                    logger.warning(f"Fecha inválida en línea {line_num}: {pub_date}")
                    date_obj = None
            else:
                date_obj = None

            doc = ScrapedDocument(
                source=data.get("source", ""),
                url=data["url"],
                title=data.get("title", ""),
                content=data["content"],
                authors=data.get("authors", []),
                date=date_obj,
            )
            scraped_docs.append(doc)

    if not scraped_docs:
        logger.warning("No se encontraron documentos en el JSONL")
        return

    logger.info(f"Generando chunks a partir de {len(scraped_docs)} documentos...")
    all_chunks = chunking_service.chunk_documents(scraped_docs)
    logger.info(f"Se generaron {len(all_chunks)} chunks en total.")

    logger.info("Indexando chunks en Elasticsearch...")
    await index_service.index_chunks(all_chunks)
    logger.info("Indexación completada correctamente.")

if __name__ == "__main__":
    asyncio.run(main())