from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Elasticsearch
    elasticsearch_hosts: list[str] = ["https://localhost:9200"]
    elasticsearch_username: str = "elastic"
    elasticsearch_password: str = "TU_PASSWORD"
    index_name: str = "scraped-docs"
    
    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "news_embeddings"
    
    # Embeddings
    embedding_model: str = "jinaai/jina-embeddings-v2-base-es"
    model_max_seq_len: int = 8192
    embedding_backend: Optional[str] = None 

    # Chunking
    chunker_max_tokens: int = 1024
    overlap_percent: int = 15
    
    class Config:
        env_file = ".env"