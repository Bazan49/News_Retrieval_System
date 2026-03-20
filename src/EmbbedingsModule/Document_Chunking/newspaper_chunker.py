from typing import List
from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument
from .chunker import Chunker
from .document_chunk import Chunk, ChunkMetadata
import re

class NewspaperChunker(Chunker):
    def __init__(self, max_tokens: int = 400, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk(self, document: ScrapedDocument) -> List[Chunk]:

        doc_id = document.url_normalized
        chunks = []

        # 1. separar por párrafos
        paragraphs = self._split_paragraphs(document.content)

        chunk_idx = 0
        for para in paragraphs:
            # 2. si el párrafo es muy largo, partirlo
            tokens = self._estimate_tokens(para)
            if tokens <= self.max_tokens:
                # párrafo corto: un solo chunk
                chunk_text = para
                chunk_metadata = ChunkMetadata(
                    doc_id=doc_id,
                    source=document.source,
                    url=document.url,
                    title=document.title,
                    publication_date=document.date,
                    chunk_type="paragraph",
                    chunk_number=chunk_idx,
                    estimated_tokens=tokens
                )
            else:
                # párrafo largo: partir en sub‑chunks con overlap
                subchunks = self._split_fixed(para, self.max_tokens, self.overlap)
                for i, sub in enumerate(subchunks):
                    chunk_text = sub
                    chunk_metadata = ChunkMetadata(
                        doc_id=doc_id,
                        source=document.source,
                        url=document.url,
                        title=document.title,
                        publication_date=document.date,
                        chunk_type="paragraph_subchunk",
                        chunk_number=chunk_idx + i,
                        estimated_tokens=self._estimate_tokens(sub)
                    )
                    chunks.append(
                        Chunk(
                            id=f"{doc_id}_{chunk_metadata.chunk_number}",
                            content=chunk_text,
                            metadata=chunk_metadata.to_dict()   
                        )
                    )
                continue  # ya metimos los subchunks, no meter el párrafo completo

            chunks.append(
                Chunk(
                    id=f"{doc_id}_{chunk_metadata.chunk_number}",
                    content=chunk_text,
                    metadata=chunk_metadata.to_dict()   
                )
            )
            chunk_idx += 1

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        # partir por doble salto de línea
        paragraphs = re.split(r"\n\s*\n", text.strip())
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_fixed(self, text: str, max_tokens: int, overlap: int) -> List[str]:
        # división por tamaño aproximado
        chunks = []
        i = 0
        while i < len(text):
            end = min(i + max_tokens, len(text))
            chunks.append(text[i:end])
            if end < len(text):
                i = end - overlap
            else:
                break
        return chunks

    def _estimate_tokens(self, text: str) -> int:
        # 1 token ≈ 4 caracteres (muy simple, sin modelos)
        return max(1, len(text) // 4)
