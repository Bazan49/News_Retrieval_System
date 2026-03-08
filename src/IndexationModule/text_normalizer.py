"""
text_normalizer.py

Módulo de procesamiento y normalización de texto en español.
"""

import re
from nltk.stem import SnowballStemmer


STOPWORDS = set([
    'a', 'al', 'algo', 'algunos', 'ante', 'aquí', 'así', 'aunque',
    'bajo', 'bien', 'bueno', 'cada', 'casi', 'como',
    'con', 'contra', 'de', 'del', 'dentro', 'desde', 'donde',
    'durante', 'el', 'ella', 'ellas', 'ellos', 'en', 'entre',
    'era', 'eran', 'es', 'esa', 'ese', 'esto', 'estos', 'estas',
    'está', 'están', 'esto', 'estoy', 'fue', 'fuera',
    'ha', 'haber', 'había', 'hace', 'hacer', 'hasta', 'hay', 'he',
    'hizo', 'hoy', 'inclusive', 'ir', 'la', 'las', 'le',
    'les', 'lo', 'los', 'más', 'mas', 'me', 'mediante',
    'menos', 'mi', 'mí', 'mia', 'mientras', 'mío', 'mis', 'mismo',
    'mucho', 'muy', 'nada', 'ni', 'no', 'nos', 'nosotros',
    'o', 'otro', 'para', 'parece', 'pero', 'poco', 'por',
    'porque', 'próximo', 'pués', 'puede', 'que', 'querer',
    'quién', 'quienes', 'quien', 'recién', 'salvo', 'se',
    'sea', 'segun', 'ser', 'será', 'serán', 'sería', 'si', 'sí',
    'siempre', 'siendo', 'sin', 'sino', 'sobre', 'solo', 'sólo',
    'somos', 'son', 'soy', 'su', 'sus', 'tal',
    'también', 'tampoco', 'tan', 'tanto', 'te', 'tenido', 'tener',
    'tenga', 'tengo', 'ti', 'tiempo', 'toda', 'todas', 'todavía',
    'todo', 'todos', 'tomar', 'tras', 'tu', 'tus', 'un',
    'una', 'uno', 'unos', 'usted', 'ustedes', 'va', 'vamos',
    'van', 'varios', 've', 'vez', 'x', 'y', 'ya', 'yo'
])


class TextNormalizer:
    
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stopwords = STOPWORDS
    
    def tokenize(self, text: str) -> list:
        if not text or not isinstance(text, str):
            return []
        
        text = text.lower()
        tokens = re.findall(r'\b[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+\b', text)
        
        return tokens
    
    def remove_punctuation(self, tokens: list) -> list:
        if not tokens:
            return []
        
        clean_tokens = []
        for token in tokens:
            clean_token = re.sub(r'[^\wáéíóúñü]', '', token)
            if clean_token:
                clean_tokens.append(clean_token)
        
        return clean_tokens
    
    def remove_stopwords(self, tokens: list) -> list:
        if not tokens:
            return []
        
        return [token for token in tokens if token not in self.stopwords]
    
    def stem(self, tokens: list) -> list:
        if not tokens:
            return []
        
        stemmed = []
        for token in tokens:
            try:
                stemmed_token = self.stemmer.stem(token)
                stemmed.append(stemmed_token)
            except Exception:
                stemmed.append(token)
        
        return stemmed
    
    def filter_by_length(self, tokens: list, min_len: int = 2, max_len: int = 30) -> list:
        if not tokens:
            return []
        
        return [token for token in tokens if min_len <= len(token) <= max_len]
    
    def normalize(self, text: str, 
                  remove_stopwords: bool = True,
                  apply_stemming: bool = True,
                  filter_length: bool = True) -> list:
        
        if not text:
            return []
        
        tokens = self.tokenize(text)
        tokens = self.remove_punctuation(tokens)
        
        if filter_length:
            tokens = self.filter_by_length(tokens)
        
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        if apply_stemming:
            tokens = self.stem(tokens)
        
        return tokens
    
    def get_term_frequencies(self, tokens: list) -> dict:
        if not tokens:
            return {}
        
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        return freq
