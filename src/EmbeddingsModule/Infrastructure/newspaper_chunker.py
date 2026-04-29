from typing import List, Tuple
from transformers import AutoTokenizer
from src.DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from ..Domain.chunker import Chunker
from ..Domain.document_chunk import Chunk, ChunkMetadata
from nltk.tokenize import sent_tokenize

class NewspaperChunker(Chunker):
    def __init__(self, max_tokens: int, overlap_percent: float, model_name: str):
        self.max_tokens = max_tokens
        self.overlap_percent = overlap_percent
        self.overlap = int(max_tokens * overlap_percent / 100)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    def chunk(self, document: ScrapedDocument) -> List[Chunk]:
        content = f"{document.title}\n\n{document.content}"
        sentences = self._split_sentences(content)

        # --- Paso 1: Convertir oraciones en unidades (texto, token_count) ---
        units = []
        for s in sentences:
            token_count = len(self.tokenizer.encode(s, add_special_tokens=True))
            if token_count <= self.max_tokens:
                units.append((s, token_count))
            else:
                # Dividir oración larga en fragmentos
                fragments = self._split_long_sentence(s, token_count, self.max_tokens)
                units.extend(fragments)   # cada fragmento es (texto, token_count)

        # --- Paso 2: Agrupar unidades en chunks respetando max_tokens y overlap ---
        chunks = []
        chunk_idx = 0
        current_units = []    # lista de (texto, token_count)
        actual_tokens = 0

        for text, token_count in units:
            if actual_tokens + token_count <= self.max_tokens:
                current_units.append((text, token_count))
                actual_tokens += token_count
            else:
                if current_units:
                    chunk = self._create_chunk_from_units(current_units, chunk_idx, actual_tokens, document)
                    chunks.append(chunk)
                    chunk_idx += 1

                # Calcular solapamiento: unidades del chunk actual que suman <= overlap
                overlap_units = self._get_overlap_units(current_units, self.overlap)
                # Nuevo chunk empieza con las unidades solapadas + la unidad que no cabía
                current_units = overlap_units + [(text, token_count)]
                actual_tokens = sum(cnt for _, cnt in current_units)

        # Último chunk
        if current_units:
            chunk = self._create_chunk_from_units(current_units, chunk_idx, actual_tokens, document)
            chunks.append(chunk)

        return chunks

    def _create_chunk_from_units(self, units: List[Tuple[str, int]], chunk_idx: int, actual_tokens: int, document: ScrapedDocument) -> Chunk:
        sentences = [text for text, _ in units]
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
        return Chunk(
            id=f"{document.url}_{chunk_metadata.chunk_number}",
            content=chunk_text,
            metadata=chunk_metadata.to_dict()
        )

    def _split_long_sentence(self, sentence: str, total_tokens: int, max_tokens: int) -> List[Tuple[str, int]]:
        """
        Divide una oración larga en fragmentos que respetan max_tokens.
        Cada fragmento es (texto, token_count).
        """
        fragments = []
        # Tokenizamos la oración completa (incluye tokens especiales [CLS] y [SEP])
        token_list = self.tokenizer.encode(sentence, add_special_tokens=True)
        start = 0
        while start < len(token_list):
            end = min(start + max_tokens, len(token_list))
            frag_tokens = token_list[start:end]
            frag_text = self.tokenizer.decode(frag_tokens, skip_special_tokens=False)
            frag_count = len(frag_tokens)
            fragments.append((frag_text, frag_count))
            start = end
        return fragments

    def _get_overlap_units(self, current_units: List[Tuple[str, int]], overlap_tokens: int) -> List[Tuple[str, int]]:
        """
        Selecciona las últimas unidades cuya suma de tokens no supere overlap_tokens.
        """
        if not current_units:
            return []
        selected = []
        total = 0
        for text, cnt in reversed(current_units):
            if total + cnt <= overlap_tokens:
                selected.insert(0, (text, cnt))
                total += cnt
            else:
                break
        return selected

    def _split_sentences(self, text: str) -> List[str]:
        sentences = sent_tokenize(text, language='spanish')
        return [s.strip() for s in sentences if s.strip()]