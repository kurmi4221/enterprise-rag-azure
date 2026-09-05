from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG API"
    environment: str = "development"
    api_version: str = "v1"

    azure_ai_project_endpoint: str

    azure_storage_account_key: str
    azure_blob_container_name: str
    azure_storage_account_url: str

    chat_deployment_name: str
    embedding_deployment_name: str

    azure_search_endpoint: str
    azure_search_index_name: str = "enterprise-documents"

    storage_account_name: str
    storage_container_name: str = "enterprise-rag-documents"

    azure_search_api_key: str

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str = "postgres"
    postgres_user: str
    postgres_password: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()