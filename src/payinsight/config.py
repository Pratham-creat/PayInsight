"""Typed application settings and shared risk thresholds."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    app_name: str = "PayInsight"
    environment: str = "development"
    database_path: str = ":memory:"
    data_dir: Path = Path("data")
    default_rows: int = Field(1000, ge=1)
    high_value_inr: float = 100_000
    velocity_limit: int = 8
    api_prefix: str = "/api"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
