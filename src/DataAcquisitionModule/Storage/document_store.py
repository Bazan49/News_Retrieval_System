import os
import hashlib
from typing import Dict, Optional

import chromadb
from typing import Any, List
from sentence_transformers import SentenceTransformer

from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument

class DocumentStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="scraped_documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def _generate_embedding(self, text: str) -> List[float]:
        return self.embedding_model.encode(text).tolist()


    def add_document(self, doc: ScrapedDocument) -> None:
        # Generar embedding
        text_for_embedding = f"{doc.title} {doc.content}"
        embedding = self._generate_embedding(text_for_embedding)

        # Preparar metadatos 
        metadata = {
            "source": doc.source or "",
            "url": doc.url,
            "url_normalized": doc.url_normalized,
            "title": doc.title,
            "authors": ", ".join(doc.authors) if doc.authors else "",
            "date": doc.date.isoformat() if doc.date else None,
            "scraped_at": doc.scraped_at.isoformat() if doc.scraped_at else "",
            "discovered_at": doc.discovered_at.isoformat() if doc.discovered_at else "",
            "indexed": doc.indexed,
            "embeddings_generated": doc.embeddings_generated,
        }

        # Eliminar claves con valor None
        metadata = {k: v for k, v in metadata.items() if v is not None}

        # Documento principal: el texto limpio (puede usarse para mostrar fragmentos)
        document_text = doc.content

        doc_id = doc.url_normalized

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document_text]
        )

        print(f" Documento almacenado: {doc.url} ")
        
    def get_document(self, url_normalized: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un documento por su URL normalizada.
        Devuelve el resultado de Chroma (incluye id, metadata, documento y embedding).
        """
        result = self.collection.get(ids=[url_normalized])
        if result and result['ids']:
            return {
                'id': result['ids'][0],
                'metadata': result['metadatas'][0] if result['metadatas'] else {},
                'document': result['documents'][0] if result['documents'] else '',
                'embedding': result['embeddings'][0] if result['embeddings'] else None
            }
        return None


    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca los documentos más similares a una consulta.
        """
        query_embedding = self._generate_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        # Reorganizar resultados en una lista de dicts
        output = []
        for i in range(len(results['ids'][0])):
            output.append({
                'id': results['ids'][0][i],
                'metadata': results['metadatas'][0][i],
                'document': results['documents'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        return output