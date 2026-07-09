from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the product API."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "HelloAgents Learn"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    database_url: str = Field(
        default="postgresql+psycopg://hello_agents:hello_agents@postgres:5432/hello_agents"
    )
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379/0"
    storage_root: Path = Path("./storage")

    request_id_header: str = "X-Request-ID"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
