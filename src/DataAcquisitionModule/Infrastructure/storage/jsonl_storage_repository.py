import json
from pathlib import Path
from DataAcquisitionModule.Domain.Interfaces.document_repository import IDocumentRepository

class JSONLRepository(IDocumentRepository):

    def __init__(self, path="data/initial_corpus.jsonl", batch_size=50):
        self.path = Path(path)
        self.buffer = []
        self.batch_size = batch_size

    def save(self, document):

        self.buffer.append({
            "source": document.source,
            "url": document.url,
            "title": document.title,
            "content": document.content
        })

        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):

        if not self.buffer:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "a", encoding="utf-8") as f:
            for doc in self.buffer:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        self.buffer = []

    def load(self):
        if not self.path.exists():
            return []

        documents = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                doc_data = json.loads(line)
                documents.append(doc_data)

        return documents