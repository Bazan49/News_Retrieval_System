import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Asegurar que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.DI.disperse_search_container import SearchContainer
from src.DI.chunking_container import ChunkingContainer
from src.DataAcquisitionModule.scrapedDocument import ScrapedDocument

# Contenedores
search_container = SearchContainer()
chunking_container = ChunkingContainer()

# Servicios
chunking_service = chunking_container.chunking_service()   # servicio de chunking
index_service = search_container.index_service()           # servicio de indexación (para chunks)

async def main():
    # Ruta al archivo JSONL
    jsonl_path = Path("data") / "initial_corpus.jsonl"
    if not jsonl_path.exists():
        print(f"❌ Archivo no encontrado: {jsonl_path}")
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
                print(f"Error JSON en línea {line_num}: {e}")
                continue

            pub_date = data.get("published_date")
            if pub_date:
                try:
                    date_obj = datetime.fromisoformat(pub_date)
                except ValueError:
                    print(f"Fecha inválida en línea {line_num}: {pub_date}")
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

    print(f"📄 Generando chunks a partir de {len(scraped_docs)} documentos...")
    # Usa el servicio de chunking para generar todos los chunks
    all_chunks = chunking_service.chunk_documents(scraped_docs)

    print(f"📦 Se generaron {len(all_chunks)} chunks en total.")

    # Indexar los chunks en Elasticsearch (el índice se crea automáticamente si no existe)
    print("🔄 Indexando chunks en Elasticsearch...")
    await index_service.index_chunks(all_chunks)
    print("✅ Indexación completada.")

if __name__ == "__main__":
    asyncio.run(main())