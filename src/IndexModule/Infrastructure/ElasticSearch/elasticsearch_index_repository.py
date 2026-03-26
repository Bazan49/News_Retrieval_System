import json
from pathlib import Path
from shlex import quote
from typing import List, Optional, Union
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from IndexModule.Domain.search_document import SearchDocument
from IndexModule.Domain.index_repository import IndexRepository

class ElasticsearchIndexRepository(IndexRepository):
    def __init__(
        self,
        client: AsyncElasticsearch,
        index_name: str,
        mapping_path: Optional[Union[str, Path]] = None,
    ):
        self.client = client
        self.index_name = index_name
        self.mapping_path = (
            Path(mapping_path)
            if mapping_path
            else Path(__file__).resolve().parent / "mapping.json"
        )
    
    async def ensure_index(self) -> None:
        """Crea índice con mapping si no existe"""
        if await self.client.indices.exists(index=self.index_name):
            return
        
        mapping = json.loads(self.mapping_path.read_text())
        await self.client.indices.create(
            index=self.index_name,
            body=mapping
        )
    
    async def index_one(self, doc: SearchDocument) -> None:
        await self.client.index(
            index=self.index_name,
            id=doc.url,
            document=doc.__dict__
        )
    
    async def index_bulk(self, docs: List[SearchDocument]) -> None:
        """Bulk indexing optimizado"""
        actions = [
            {
                "_index": self.index_name,
                "_id": doc.url,
                "_source": doc.__dict__
            }
            for doc in docs
        ]
        await async_bulk(self.client, actions)
    
    async def delete_by_id(self, doc_id: str) -> None:
        await self.client.delete(
            index=self.index_name,
            id=doc_id
        )
    
    async def refresh(self) -> None:
        await self.client.indices.refresh(index=self.index_name)

    async def get_term_frequency(
        self, 
        doc_id: str, 
        field: str, 
        term: str
    ) -> int:
        """Frecuencia EXACTA de un término en un documento específico"""
        encoded_id = quote(doc_id)
        
        tv = await self.client.termvectors(
            index=self.index_name,
            id=encoded_id,
            fields=[field],
            term_statistics=False
        )
        
        if 'term_vectors' in tv and field in tv['term_vectors']:
            terms = tv['term_vectors'][field].get('terms', {})
            return terms.get(term, {}).get('term_freq', 0)
        
        return 0