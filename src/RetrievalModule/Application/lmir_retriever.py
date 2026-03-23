"""
Módulo de Puntuación LMIR - Modelo Probabilístico de Lenguaje

Este módulo implementa la función de puntuación:
    P(Q|D) según el Modelo Query Likelihood con Suavizado Dirichlet

Fórmula:
    P(w|D) = (tf(w,D) + μ × P(w|C)) / (|D| + μ)
    P(Q|D) = ∏ P(w|D)  para cada w en Q
    log P(Q|D) = Σ log P(w|D)

Donde:
    - tf(w,D): frecuencia del término w en documento D
    - P(w|C): probabilidad del término w en la colección
    - μ: parámetro de suavizado Dirichlet
    - |D|: longitud del documento
"""

import math
from typing import List, Dict, Tuple
from collections import Counter


class LMIRScoreFunction:
    """
    Función de puntuación P(Q|D) usando Suavizado Dirichlet.
    
    esta clase es usada para:
    - Calcular P(Q|D) para cualquier documento
    - Obtener estadísticas del modelo
    - Verificación matemática unitaria
    """
    
    def __init__(self, mu: float = 1000.0):
        """
        Args:
            mu: Parámetro de suavizado Dirichlet (default: 1000)
        """
        self.mu = mu
        self._initialized = False
        self._doc_term_freqs: Dict[str, Counter] = {}
        self._doc_lengths: Dict[str, int] = {}
        self._collection_freq: Counter = Counter()
        self._total_tokens: int = 0
        self._collection_prob: Dict[str, float] = {}
    
    def load_statistics(
        self,
        doc_term_freqs: Dict[str, Counter],
        doc_lengths: Dict[str, int],
        collection_freq: Counter
    ) -> None:
        """
        Carga las estadísticas necesarias para calcular P(Q|D).
        
        Args:
            doc_term_freqs: {doc_id: Counter({term: tf})} - Frecuencias por documento
            doc_lengths: {doc_id: length} - Longitud de cada documento
            collection_freq: Counter({term: freq}) - Frecuencia total en colección
        """
        self._doc_term_freqs = doc_term_freqs
        self._doc_lengths = doc_lengths
        self._collection_freq = collection_freq
        self._total_tokens = sum(collection_freq.values())
        
        for term, freq in collection_freq.items():
            self._collection_prob[term] = freq / self._total_tokens
        
        self._initialized = True
    
    def compute_p_w_given_d(self, term: str, doc_id: str) -> float:
        """
        Calcula P(w|D) para un término específico.
        
        P(w|D) = (tf(w,D) + μ × P(w|C)) / (|D| + μ)
        
        Args:
            term: Término a evaluar
            doc_id: ID del documento
            
        Returns:
            P(w|D)
        """
        tf = self._doc_term_freqs.get(doc_id, Counter()).get(term, 0)
        doc_len = self._doc_lengths.get(doc_id, 0)
        p_w_c = self._collection_prob.get(term, 0.0)
        
        if doc_len == 0:
            return 0.0
        
        p_w_d = (tf + self.mu * p_w_c) / (doc_len + self.mu)
        return p_w_d
    
    def compute_log_p_query_given_doc(self, query_tokens: List[str], doc_id: str) -> float:
        """
        Calcula log P(Q|D) para una query.
        
        log P(Q|D) = Σ log P(w|D)
        
        Args:
            query_tokens: Lista de términos de la query (ya tokenizados)
            doc_id: ID del documento
            
        Returns:
            log P(Q|D)
        """
        score = 0.0
        for term in query_tokens:
            p_w_d = self.compute_p_w_given_d(term, doc_id)
            if p_w_d > 0:
                score += math.log(p_w_d)
            else:
                return float('-inf')
        return score
    
    def score_document(self, query_tokens: List[str], doc_id: str) -> Dict:
        """
        Retorna el score completo con desglose matemático.
        
        Útil para verificar la corrección del cálculo.
        
        Args:
            query_tokens: Lista de términos de la query
            doc_id: ID del documento
            
        Returns:
            Diccionario con todos los cálculos intermedios
        """
        doc_len = self._doc_lengths.get(doc_id, 0)
        term_scores = []
        total_score = 0.0
        
        for term in query_tokens:
            tf = self._doc_term_freqs.get(doc_id, Counter()).get(term, 0)
            p_w_c = self._collection_prob.get(term, 0.0)
            p_w_d = self.compute_p_w_given_d(term, doc_id)
            log_p = math.log(p_w_d) if p_w_d > 0 else float('-inf')
            
            term_scores.append({
                "term": term,
                "tf": tf,
                "p_w_c": p_w_c,
                "p_w_d": p_w_d,
                "log_p_w_d": log_p
            })
            total_score += log_p
        
        return {
            "doc_id": doc_id,
            "doc_length": doc_len,
            "mu": self.mu,
            "term_scores": term_scores,
            "log_p_query_given_doc": total_score,
            "p_query_given_doc": math.exp(total_score) if total_score > float('-inf') else 0.0
        }
    
    def get_statistics(self) -> Dict:
        """
        Retorna estadísticas del modelo.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self._initialized:
            return {"error": "No statistics loaded"}
        
        num_docs = len(self._doc_lengths)
        avg_doc_length = self._total_tokens / num_docs if num_docs > 0 else 0
        
        return {
            "num_documents": num_docs,
            "vocabulary_size": len(self._collection_freq),
            "total_collection_tokens": self._total_tokens,
            "average_document_length": avg_doc_length,
            "mu": self.mu
        }
    
    def get_term_stats(self, term: str) -> Dict:
        """
        Retorna estadísticas de un término específico.
        
        Args:
            term: Término a consultar
            
        Returns:
            Diccionario con estadísticas del término
        """
        if not self._initialized:
            return {"error": "No statistics loaded"}
        
        coll_freq = self._collection_freq.get(term, 0)
        p_w_c = self._collection_prob.get(term, 0.0)
        
        doc_count = sum(
            1 for doc_tf in self._doc_term_freqs.values()
            if term in doc_tf
        )
        
        return {
            "term": term,
            "collection_frequency": coll_freq,
            "p_w_c": p_w_c,
            "document_frequency": doc_count,
            "num_documents": len(self._doc_lengths)
        }
