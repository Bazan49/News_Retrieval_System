import sys
import os
import argparse
from pathlib import Path

# Asegura que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logging_config import setup_logging
setup_logging()
from src.DataAcquisitionModule.data_acquisition_service import DataAcquisitionService

def parse_args():
    parser = argparse.ArgumentParser(description="Recolector de noticias")
    parser.add_argument("--max-pages", type=int, default=int(os.getenv("MAX_PAGES", "15")),
                        help="Número máximo de páginas a scrapear")
    parser.add_argument("--max-depth", type=int, default=int(os.getenv("MAX_DEPTH", "3")),
                        help="Profundidad máxima de crawling")
    parser.add_argument("--delay", type=int, default=int(os.getenv("DELAY", "1")),
                        help="Segundos de espera entre peticiones")
    parser.add_argument("--batch-size", type=int, default=int(os.getenv("BATCH_SIZE", "10")),
                        help="Tamaño del lote para guardar en JSONL")
    parser.add_argument("--output-file", type=str, default=os.getenv("OUTPUT_FILE", "data/corpus.jsonl"),
                        help="Ruta del archivo de salida (JSONL)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    # Asegurar que el directorio de salida existe
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    service = DataAcquisitionService(
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        batch_size=args.batch_size,
        output_file=args.output_file
    )
    service.run()