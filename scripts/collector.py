import sys
from pathlib import Path

# Asegura que el paquete `src/` esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.DataAcquisitionModule.data_acquisition_service import DataAcquisitionService

if __name__ == "__main__":
    service = DataAcquisitionService(max_pages=50, max_depth=3, delay=1, batch_size=10, output_file="data/corpus.jsonl")
    service.run()