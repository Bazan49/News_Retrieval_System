from typing import List, Optional
from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument
from DataAcquisitionModule.Storage.document_store import DocumentStore
from inverted_index import InvertedIndex

class Indexer:
    def __init__(self, document_store: DocumentStore, normalizer):
        self.doc_store = document_store
        self.normalizer = normalizer
        self.inverted_index = InvertedIndex()

    def index_document(self, doc: ScrapedDocument):
        """
        Indexa un documento: extrae texto, normaliza, agrega al índice invertido.
        """
        # Obtener texto a indexar (título + contenido)
        text = f"{doc.title} {doc.content}"
        tokens = self.normalizer.normalize(text)

        # Agregar al índice invertido
        self.inverted_index.add_document(doc.url_normalized, tokens)

    def bulk_index(self, documents: List[ScrapedDocument]):
        """Indexa múltiples documentos."""
        for doc in documents:
            self.index_document(doc)

    def search(self, query: str, top_k: int = 10) -> List[dict]:
        """
        Busca documentos usando el índice invertido y enriquece con metadatos del DocumentStore.
        Retorna lista de diccionarios con información del documento y score.
        """
        # Tokenizar consulta
        query_tokens = self.normalizer.normalize(query)

        # Obtener resultados del índice invertido
        results = self.inverted_index.search(query_tokens)

        # Limitar a top_k
        results = results[:top_k]

        # Enriquecer con información
        enriched = []
        for doc_id, score in results:
            doc_info = self.doc_store.get_document(doc_id)
            if doc_info:
                enriched.append({
                    'doc_id': doc_id,
                    'score': score,
                    'title': doc_info.get('metadata', {}).get('title', ''),
                    'url': doc_info.get('metadata', {}).get('url', ''),
                    'snippet': doc_info.get('document', '')[:200] + '...'  # fragmento
                })
            else:
                enriched.append({
                    'doc_id': doc_id,
                    'score': score,
                    'title': '',
                    'url': '',
                    'snippet': ''
                })
        return enriched