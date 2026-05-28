from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Elasticsearch
    elasticsearch_hosts: list[str] = ["https://localhost:9200"]
    elasticsearch_username: str = "elastic"
    elasticsearch_password: str = "TU_PASSWORD"
    index_name: str = "news-chunks"
    
    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "news_embeddings"
    
    # Embeddings
    embedding_model: str = "jinaai/jina-embeddings-v2-base-es"
    model_max_seq_len: int = 8192
    embedding_backend: Optional[str] = None 
    # Chunking
    chunker_max_tokens: int = 512
    overlap_percent: int = 15

    # WebSearchModule 
    google_news_lang: str = "es-419"
    google_news_country: str = "US"

    # RAG - Groq
    groq_api_key: Optional[str] = None
    groq_model_id: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 700
    groq_frequency_penalty: float = 0.5
    groq_presence_penalty: float = 0.3
    groq_top_p: float = 0.95
    
    # RAG - ContextBuilder
    rag_max_chunks: int = 10
    rag_max_chunks_per_doc: int = 2


    # Umbral para considerar un resultado local como "bueno" (RRF score)
    good_rrf_threshold: float = 0.01
    
    # Umbral mínimo de longitud de contenido para considerar un resultado válido
    min_content_length: int = 50

    #Refinement
    refinement_top_n: int = 5

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"