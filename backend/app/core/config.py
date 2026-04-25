from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    app_name: str = "case-shift-backend"
    environment: Literal["development", "production", "testing"] = "development"
    debug: bool = True

    # Optional URL configurations with defaults
    redis_url: str = "redis://localhost:6379/0"
    falkordb_url: str = "redis://localhost:6379/0"
    falkordb_graph_name: str = "case_shift"
    s3_endpoint_url: str = "http://localhost:4566"
    s3_bucket_name: str = "case-shift-artifacts"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
