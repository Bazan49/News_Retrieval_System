"""
Poblar ChromaDB con los embeddings de los chunks generados a partir del corpus.
Lee desde el archivo JSONL, crea ScrapedDocuments, genera chunks y los indexa.
"""

import argparse
import sys
import asyncio
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Asegurar que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar logging (puedes usar setup_logging si ya existe)
from src.logging_config import setup_logging
setup_logging()
logger = logging.getLogger("PopulateChromaDB")

from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument
from src.DI.embeddings_container import EmbeddingsContainer
from src.DI.chunking_container import ChunkingContainer
from src.DI.config_container import ConfigContainer

def parse_args():
    parser = argparse.ArgumentParser(description="Poblar ChromaDB a partir de un archivo JSONL")
    parser.add_argument("--input-file", type=str, default="data/initial_corpus.jsonl",
                        help="Ruta al archivo JSONL de entrada (por defecto: data/initial_corpus.jsonl)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Número máximo de documentos a procesar (0 = todos)")
    return parser.parse_args()

# Contenedores
_config_container = ConfigContainer()
_embeddings_container = EmbeddingsContainer()
_chunking_container = ChunkingContainer()

_embeddings_container.override_providers(
    settings=_config_container.settings,
)

_chunking_container.override_providers(
    settings=_config_container.settings,
)

# Servicios
chunking_service = _chunking_container.chunking_service()
index_service = _embeddings_container.vector_indexer()

async def main():
    args = parse_args()
    jsonl_path = Path(args.input_file)
    limit = args.limit if args.limit > 0 else None

    logger.info(f"Iniciando población de ChromaDB desde: {jsonl_path}")
    if limit:
        logger.info(f"Limitando a {limit} documentos")

    if not jsonl_path.exists():
        logger.error(f"Archivo no encontrado: {jsonl_path}")
        return

    # Leer documentos
    scraped_docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if limit and len(scraped_docs) >= limit:
                break
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
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
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

    logger.info(f"Cargados {len(scraped_docs)} documentos desde JSONL")

    # Generar chunks
    logger.info("Generando chunks...")
    all_chunks = chunking_service.chunk_documents(scraped_docs)
    logger.info(f"Se generaron {len(all_chunks)} chunks")

    # Indexar en ChromaDB
    try:
        start = time.perf_counter()
        total_chunks = await index_service.index_chunks(all_chunks)
        elapsed = time.perf_counter() - start
        logger.info(f"Indexación completada. {total_chunks} chunks en {elapsed:.2f} segundos")
    except Exception as e:
        logger.error(f"Error durante la indexación: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())