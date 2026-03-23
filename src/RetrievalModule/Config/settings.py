from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrievalSettings(BaseSettings):
    lmir_mu: float = 1000.0
    default_top_k: int = 10
    
    model_config = SettingsConfigDict(extra="ignore")
