"""
Poblar ChromaDB con los embeddings de los chunks generados a partir del corpus.
Lee desde el archivo JSONL, crea ScrapedDocuments, genera chunks y los indexa.
"""

import sys
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Asegura que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument
from src.DI.embeddings_container import EmbeddingsContainer
from src.DI.chunking_container import ChunkingContainer

async def main():
    print("🚀 Iniciando población de ChromaDB...")

    # Contenedores
    embeddings_container = EmbeddingsContainer()
    chunking_container = ChunkingContainer()

    # Servicios
    try:
        indexer = embeddings_container.vector_indexer()
        chunking_service = chunking_container.chunking_service()
        print("✅ Container, VectorIndexer y ChunkingService creados")
    except Exception as e:
        print(f"❌ Error creando servicios: {e}")
        return

    # Ruta al archivo JSONL
    jsonl_path = Path("data") / "initial_corpus.jsonl"
    if not jsonl_path.exists():
        print(f"❌ Archivo no encontrado: {jsonl_path}")
        return

    # Leer documentos
    scraped_docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            pub_date = data.get("published_date")
            if pub_date:
                pub_date = pub_date.replace('Z', '+00:00')
                try:
                    date_obj = datetime.fromisoformat(pub_date)
                except ValueError:
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
        print("No se encontraron documentos en el JSONL")
        return

    print(f"📄 Cargados {len(scraped_docs)} documentos desde JSONL")

    N = 0  # Cambia a N > 0 para procesar solo una parte de los documentos
    if N > 0:
        scraped_docs = scraped_docs[:N]
        print(f"📄 Limitando a {N} documentos para prueba rápida")

    # Generar chunks a partir de los documentos
    print("🔄 Generando chunks...")
    all_chunks = chunking_service.chunk_documents(scraped_docs)
    print(f"📦 Se generaron {len(all_chunks)} chunks")

    # Indexar en ChromaDB
    try:
        start = time.perf_counter()
        total_chunks = await indexer.index_chunks(all_chunks)
        elapsed = time.perf_counter() - start
        print(f"✅ Indexación completada. {total_chunks} chunks en {elapsed:.2f} segundos")
    except Exception as e:
        print(f"❌ Error durante la indexación: {e}")

if __name__ == "__main__":
    asyncio.run(main())