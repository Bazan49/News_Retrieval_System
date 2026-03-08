"""
text_index.py

Índice invertido para contenido textual.
"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_index import BaseIndex


STOPWORDS = {'el', 'la', 'de', 'que', 'en', 'un', 'una', 'por', 'para', 
             'con', 'sin', 'sobre', 'entre', 'es', 'son', 'está', 'están'}


class TextIndex(BaseIndex):
    """Índice invertido para contenido textual."""
    
    def __init__(self):
        super().__init__()
        self.inverted_index: Dict[str, set] = {}
        self.doc_term_freq: Dict[str, Dict[str, int]] = {}
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        if not content or not isinstance(content, str):
            return
        
        tokens = self._tokenize(content)
        term_freq = self._calculate_term_frequency(tokens)
        
        doc_data = {
            'id': doc_id,
            'content': content,
            'tokens': tokens,
            'term_freq': term_freq,
            'metadata': metadata or {},
            'added_at': datetime.utcnow().isoformat()
        }
        
        self.documents[doc_id] = doc_data
        self.doc_term_freq[doc_id] = term_freq
        
        for token in set(tokens):
            if token not in self.inverted_index:
                self.inverted_index[token] = set()
            self.inverted_index[token].add(doc_id)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        if not query:
            return []
        
        query_tokens = self._tokenize(query)
        
        doc_scores = {}
        for token in query_tokens:
            if token in self.inverted_index:
                for doc_id in self.inverted_index[token]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = self.documents.get(doc_id, {})
            results.append({
                'id': doc_id,
                'score': score,
                'content': doc.get('content', '')[:200],
                'metadata': doc.get('metadata', {})
            })
        
        return results
    
    def remove_document(self, doc_id: str) -> bool:
        if doc_id not in self.documents:
            return False
        
        tokens = self.documents[doc_id].get('tokens', [])
        
        for token in tokens:
            if token in self.inverted_index:
                self.inverted_index[token].discard(doc_id)
                if not self.inverted_index[token]:
                    del self.inverted_index[token]
        
        del self.documents[doc_id]
        self.doc_term_freq.pop(doc_id, None)
        
        return True
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        return self.documents.get(doc_id)
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\b[a-záéíóúñü]+\b', text)
        return [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    
    def _calculate_term_frequency(self, tokens: List[str]) -> Dict[str, int]:
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        return freq
    
    def get_terms(self) -> List[str]:
        return list(self.inverted_index.keys())
    
    def from_dict(self, data: Dict) -> None:
        self.documents = data.get('documents', {})
        
        self.inverted_index = {}
        self.doc_term_freq = {}
        
        for doc_id, doc in self.documents.items():
            tokens = doc.get('tokens', [])
            self.doc_term_freq[doc_id] = doc.get('term_freq', {})
            
            for token in set(tokens):
                if token not in self.inverted_index:
                    self.inverted_index[token] = set()
                self.inverted_index[token].add(doc_id)
