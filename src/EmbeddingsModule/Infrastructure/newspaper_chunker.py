from typing import List

import nltk
from src.DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from ..Domain.chunker import Chunker
from ..Domain.document_chunk import Chunk, ChunkMetadata
import tiktoken
from nltk.tokenize import sent_tokenize

class NewspaperChunker(Chunker):
    def __init__(self, max_tokens=420, overlap=80, model_name="gpt-3.5-turbo"):

        # # Descargar recursos de NLTK si no existen
        # try:
        #     nltk.data.find('tokenizers/punkt')
        # except LookupError:
        #     nltk.download('punkt', quiet=True)
            
        self.max_tokens = max_tokens 
        self.overlap = overlap 
        self.encoder = tiktoken.encoding_for_model(model_name)

    def chunk(self, document: ScrapedDocument) -> List[Chunk]:

        chunks = []

        content = f"{document.title}\n\n{document.content}"

        # 1. separar por oraciones 
        sentences = self._split_sentences(content)

        chunk_idx = 0

        current_sentences = []
        actual_tokens = 0

        for sentence in sentences:

            tokens = self._estimate_tokens(sentence)

            if(tokens + actual_tokens) <= self.max_tokens: # si la frase cabe en el chunk actual, la agregamos
                current_sentences.append(sentence)
                actual_tokens += tokens

            else: # si no cabe, creamos un nuevo chunk con lo que tenemos hasta ahora y empezamos con la nueva frase
                chunk = self.create_chunk(current_sentences, chunk_idx, actual_tokens, document)
                chunks.append(chunk)

                # preparamos el siguiente chunk, con overlap
                overlap_sentences = self._smart_overlap(current_sentences)
                current_sentences = overlap_sentences + [sentence] # el nuevo chunk empieza con el overlap
                actual_tokens = sum(self._estimate_tokens(s) for s in current_sentences)

                chunk_idx += 1

        if(current_sentences): # si quedó algo sin agregar, lo agregamos como un último chunk

            chunk = self.create_chunk(current_sentences, chunk_idx, actual_tokens, document)
            chunks.append(chunk)

        return chunks
    
    def create_chunk(self, sentences: List[str], chunk_idx, actual_tokens, document: ScrapedDocument) -> Chunk:
        # Implementación específica para crear chunks a partir de oraciones

        chunk_text = " ".join(sentences)
        chunk_metadata = ChunkMetadata(
            doc_id=document.url,
            source=document.source,
            title=document.title,
            publication_date=document.date,
            authors=document.authors,
            chunk_number=chunk_idx,
            estimated_tokens=actual_tokens
        )

        chunk = Chunk(
                id=f"{document.url}_{chunk_metadata.chunk_number}",
                content=chunk_text,
                metadata=chunk_metadata.to_dict()   
            )
        
        return chunk
    
    def _split_sentences(self, text: str) -> List[str]:
        """NLTK sent_tokenize español - 99% precisión"""
        sentences = sent_tokenize(text, language='spanish')  
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def _smart_overlap(self, current_sentences: List[str]) -> List[str]:
        """Overlap híbrido inteligente"""

        if not current_sentences:
            return []
        
        last_sentence = current_sentences[-1]
        last_tokens = self._estimate_tokens(last_sentence)
        
        if last_tokens < 20 and len(current_sentences) >= 2:
            # Muy corta → 2 últimas oraciones
            
            two_last_text = " ".join(current_sentences[-2:])
            two_last_tokens = self._estimate_tokens(two_last_text)
            if two_last_tokens <= 80:  # ← límite seguro
                return current_sentences[-2:]
            
        if last_tokens > self.overlap:
            # Muy larga → últimos overlap tokens
            return [self._get_last_n_tokens(last_sentence, self.overlap)]
        
        # Mediana → oración completa
        return [last_sentence]

    def _get_last_n_tokens(self, text: str, n_tokens: int) -> str:
        """Extrae últimos N tokens"""
        encoded = self.encoder.encode(text)
        last_n = encoded[-n_tokens:] if len(encoded) > n_tokens else encoded
        return self.encoder.decode(last_n)
