import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Asegura que el paquete `src/` esté en el path
ROOT = Path(__file__).resolve().parent.parent 
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from DI.continer import SearchContainer
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument

container = SearchContainer()
container.wire(modules=[__name__])

async def main():
    index_service = container.index_service()
    
    # Ruta al archivo JSONL con los documentos a indexar
    jsonl_path = ROOT / "data" / "initial_corpus.jsonl"  
    
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
            
            # Convertir fecha ISO a datetime (puede venir como None)
            pub_date = data.get("published_date")
            if pub_date:
                try:
                    date_obj = datetime.fromisoformat(pub_date)
                except ValueError:
                    print(f"Fecha inválida en línea {line_num}: {pub_date}")
                    date_obj = None
            else:
                date_obj = None
            
            # Construir ScrapedDocument
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
    
    print(f"Indexando {len(scraped_docs)} documentos...")
    await index_service.index_scraped_documents(scraped_docs)
    print("✅ Indexación completada")

if __name__ == "__main__":
    asyncio.run(main())