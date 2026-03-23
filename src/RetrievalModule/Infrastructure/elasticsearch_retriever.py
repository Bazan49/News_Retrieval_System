"""
ElasticsearchRetriever - Acceso a documentos de Elasticsearch
"""

from typing import List, Optional
from dataclasses import dataclass
from elasticsearch import AsyncElasticsearch
import asyncio


@dataclass
class DocumentData:
    doc_id: str
    url: str
    title: str
    content: str
    source: str


class ElasticsearchRetriever:
    """Obtiene documentos de Elasticsearch."""
    
    def __init__(self, client: AsyncElasticsearch, index_name: str, fetch_size: int = 100):
        self.client = client
        self.index_name = index_name
        self.fetch_size = fetch_size
    
    async def get_all_documents(self) -> List[DocumentData]:
        """Obtiene todos los documentos del índice."""
        documents = []
        search_after = None
        
        while True:
            query = {
                "size": self.fetch_size,
                "sort": [{"_id": "asc"}],
                "query": {"match_all": {}},
                "_source": ["url", "title", "content", "source"]
            }
            if search_after:
                query["search_after"] = search_after
            
            response = await self.client.search(index=self.index_name, body=query)
            hits = response.get("hits", {}).get("hits", [])
            
            if not hits:
                break
            
            for hit in hits:
                source = hit.get("_source", {})
                documents.append(DocumentData(
                    doc_id=hit["_id"],
                    url=source.get("url", ""),
                    title=source.get("title", ""),
                    content=source.get("content", ""),
                    source=source.get("source", "")
                ))
            
            search_after = hits[-1].get("sort")
            if len(hits) < self.fetch_size:
                break
        
        return documents
    
    async def count(self) -> int:
        """Cuenta documentos en el índice."""
        response = await self.client.count(index=self.index_name)
        return response.get("count", 0)
