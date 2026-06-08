from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    qdrant_url: str = "http://localhost:6533"
    qdrant_collection_name: str = "document_chunks"

    class Config:
        env_file = ".env"


settings = Settings()
