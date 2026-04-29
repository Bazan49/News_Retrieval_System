"""
Poblar ChromaDB con los embeddings de los documentos del corpus.
Lee desde el archivo JSONL, crea ScrapedDocuments y usa VectorIndexer asíncrono.
"""

import sys
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Asegura que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from src.DI.embeddings_container import EmbeddingsContainer

async def main():

    print("🚀 Iniciando población de ChromaDB...")

    # Crear contenedor 
    container = EmbeddingsContainer()

    # Obtener indexador asíncrono
    try:
        indexer = container.vector_indexer()
        print("✅ Container y VectorIndexer creados")
    except Exception as e:
        print(f"❌ Error creando container: {e}")
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

    N = 10  # Cambia a 0 para procesar todos
    if N > 0:
        scraped_docs = scraped_docs[:N]
        print(f"📄 Limitando a {N} documentos para prueba rápida")

    # Indexar (asíncrono)
    try:
        start = time.perf_counter()
        total_chunks = await indexer.index(scraped_docs)
        elapsed = time.perf_counter() - start
        print(f"✅ Indexación completada. {total_chunks} chunks en {elapsed:.2f} segundos")
    except Exception as e:
        print(f"❌ Error durante la indexación: {e}")

if __name__ == "__main__":
    asyncio.run(main())