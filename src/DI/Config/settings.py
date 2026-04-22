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
    chroma_port: int = 8000
    chroma_collection: str = "news_embeddings"
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_backend: Optional[str] = None  
    
    class Config:
        env_file = ".env"