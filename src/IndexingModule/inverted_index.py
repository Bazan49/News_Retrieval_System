import math
from collections import defaultdict
from typing import List, Tuple

class InvertedIndex:
    def __init__(self):
        # índice invertido: término -> {doc_id: tf}
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_length = {}          # doc_id -> número de términos en el documento
        self.doc_count = 0             # número total de documentos
        self.term_doc_freq = defaultdict(int)  # término -> cantidad de docs que lo contienen (df)

    def add_document(self, doc_id: str, tokens: List[str]):
        """
        Agrega un documento al índice.
        tokens: lista de términos normalizados.
        """
        # Contar frecuencias en el documento
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1

        # Actualizar índice invertido y df
        for term, freq in term_freq.items():
            self.index[term][doc_id] = freq
            self.term_doc_freq[term] += 1

        # Guardar longitud del documento
        self.doc_length[doc_id] = len(tokens)
        self.doc_count += 1

    def remove_document(self, doc_id: str):
        """Elimina un documento del índice."""
        
        # Buscar todos los términos que contienen este doc_id
        terms_to_remove = []
        for term, docs in self.index.items():
            if doc_id in docs:
                del docs[doc_id]
                self.term_doc_freq[term] -= 1
                if not docs: 
                    terms_to_remove.append(term)
        
        for term in terms_to_remove:
            del self.index[term]
            del self.term_doc_freq[term]

        if doc_id in self.doc_length:
            del self.doc_length[doc_id]
            self.doc_count -= 1

    def search(self, query_tokens: List[str]) -> List[Tuple[str, float]]:
        """
        Busca documentos relevantes para la consulta usando TF-IDF.
        Retorna lista de (doc_id, score) ordenada por score descendente.
        """
        # Calcular IDF para cada término de la consulta
        idf = {}
        for term in set(query_tokens):
            df = self.term_doc_freq.get(term, 0)
            idf[term] = math.log((self.doc_count + 1) / (df + 1)) + 1

        # Calcular scores para cada documento
        scores = defaultdict(float)
        for term in query_tokens:
            if term in self.index:
                for doc_id, tf in self.index[term].items():
                    # TF normalizado
                    tf_weight = 1 + math.log(tf) if tf > 0 else 0
                    scores[doc_id] += tf_weight * idf[term]

        # Ordenar por puntuación descendente
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores