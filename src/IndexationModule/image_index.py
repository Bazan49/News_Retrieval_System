"""
image_index.py

Índice para metadatos de imágenes.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_index import BaseIndex


class ImageIndex(BaseIndex):
    """Índice para metadatos de imágenes."""
    
    def __init__(self):
        super().__init__()
    
    def add_document(self, doc_id: str, content: Any, metadata: Optional[Dict] = None) -> None:
        if metadata is None:
            metadata = {}
        
        if isinstance(content, dict):
            metadata.update(content)
        elif isinstance(content, str):
            metadata['description'] = content
        
        doc_data = {
            'id': doc_id,
            'content': content,
            'metadata': metadata,
            'added_at': datetime.utcnow().isoformat()
        }
        
        self.documents[doc_id] = doc_data
    
    def search(self, query: Dict, top_k: int = 10) -> List[Dict]:
        results = []
        
        for doc_id, doc in self.documents.items():
            score = 0
            metadata = doc.get('metadata', {})
            
            if 'tags' in query:
                doc_tags = set(metadata.get('tags', []))
                query_tags = set(query['tags']) if isinstance(query['tags'], list) else {query['tags']}
                score += len(doc_tags.intersection(query_tags))
            
            if 'description' in query:
                if query['description'].lower() in metadata.get('description', '').lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'id': doc_id,
                    'score': score,
                    'metadata': metadata
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def remove_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        return self.documents.get(doc_id)
    
    def from_dict(self, data: Dict) -> None:
        self.documents = data.get('documents', {})
