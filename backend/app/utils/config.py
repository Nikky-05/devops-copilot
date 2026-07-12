from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )

    # LLM provider selection: "anthropic" | "ollama"
    llm_provider: str = "anthropic"

    # Anthropic (Step 3)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-7"

    # Ollama (local, alternative to Anthropic)
    ollama_model: str = "llama3.2:3b"
    ollama_base_url: str = "http://localhost:11434"

    # RAG / ChromaDB (Step 4)
    chroma_db_path: str = "./chroma_db"
    chroma_collection: str = "devops_docs"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 4

    # MCP integrations (Step 5, optional)
    github_token: str = ""
    postgres_url: str = ""
    kubeconfig_path: str = ""
    filesystem_root: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
