import os
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

    # RAG 
    mistral_api_key: str  # Mistral API key

    model_id: str = "mistral-small-latest"
    temperature: float = 0.3
    max_tokens: int = 500
    frequency_penalty: float = 0.5
    presence_penalty: float = 0.3
    top_p: float = 0.95
    
    # RAG - ContextBuilder
    rag_max_chunks: int = 10
    rag_max_chunks_per_doc: int = 2

    #Refinement
    refinement_top_n: int = 5

    # WebSearchModule 
    google_news_lang: str = "es-419"
    google_news_country: str = "US"

    # Umbral para considerar un resultado local como "bueno" (RRF score)
    good_rrf_threshold: float = 0.01
    
    # Umbral mínimo de longitud de contenido para considerar un resultado válido
    min_content_length: int = 50

    # Authentication JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    #  Ranking y Posicionamiento 
    rrf_k: int = 60
    w_relevance: float = 0.5
    w_personalization: float = 0.25
    w_recency: float = 0.25
    recency_decay_days: int = 30
    cross_encoder_model_name_or_path: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    activate_cross_encoder_for_relevance: bool = True
    
    # SQLite paths (no configurables desde .env)
    @property
    def sqlite_folder(self) -> str:
        return "sqlite_data"

    @property
    def feedback_db_path(self) -> str:
        return os.path.join(self.sqlite_folder, "feedback.db")

    @property
    def search_history_db_path(self) -> str:
        return os.path.join(self.sqlite_folder, "search_history.db")

    @property
    def users_db_path(self) -> str:
        return os.path.join(self.sqlite_folder, "users.db")
    
    class Config:
        env_file = ".env"