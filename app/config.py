import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str = "企业员工管理系统"
    version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = "password"
    name: str = "test_db3"
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        return (
            f"mysql+pymysql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}?charset=utf8mb4"
        )

    @property
    def async_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}?charset=utf8mb4"
        )


class SecurityConfig(BaseModel):
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120


class CorsConfig(BaseModel):
    allow_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8001",
    ]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class RateLimitConfig(BaseModel):
    enabled: bool = True
    requests_per_minute: int = 60


class RAGConfig(BaseModel):
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    collection_name: str = "eems_documents"
    persist_directory: str = "./data/chroma_db"
    chunk_size: int = 800
    chunk_overlap: int = 50
    top_k: int = 5
    similarity_threshold: float = 0.3


class AdminConfig(BaseModel):
    username: str = "admin"
    password: str = "admin123456"
    role_name: str = "系统管理员"


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    security: SecurityConfig = SecurityConfig()
    cors: CorsConfig = CorsConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    rag: RAGConfig = RAGConfig()
    admin: AdminConfig = AdminConfig()

    @property
    def database_url(self) -> str:
        return self.database.url

    @property
    def async_database_url(self) -> str:
        return self.database.async_url


def load_config_from_yaml(config_path: str | Path | None = None) -> dict[str, Any]:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    else:
        config_path = Path(config_path)
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_env_overrides() -> dict[str, Any]:
    overrides: dict[str, Any] = {}

    def _set_nested(data: dict[str, Any], keys: list[str], value: Any) -> None:
        current = data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    env_mappings = {
        "APP_NAME": ["app", "name"],
        "APP_VERSION": ["app", "version"],
        "APP_DEBUG": ["app", "debug"],
        "APP_HOST": ["app", "host"],
        "APP_PORT": ["app", "port"],
        "DATABASE_HOST": ["database", "host"],
        "DATABASE_PORT": ["database", "port"],
        "DATABASE_USERNAME": ["database", "username"],
        "DATABASE_PASSWORD": ["database", "password"],
        "DATABASE_NAME": ["database", "name"],
        "SECRET_KEY": ["security", "secret_key"],
        "ALGORITHM": ["security", "algorithm"],
        "ACCESS_TOKEN_EXPIRE_MINUTES": ["security", "access_token_expire_minutes"],
        "RAG_EMBEDDING_MODEL": ["rag", "embedding_model"],
        "RAG_PERSIST_DIRECTORY": ["rag", "persist_directory"],
        "ADMIN_USERNAME": ["admin", "username"],
        "ADMIN_PASSWORD": ["admin", "password"],
    }

    for env_key, path in env_mappings.items():
        val = os.getenv(env_key)
        if val is not None:
            if env_key.endswith("_DEBUG"):
                val = val.lower() == "true"
            elif env_key.endswith("_PORT"):
                val = int(val)
            _set_nested(overrides, path, val)

    return overrides


def _deep_merge(base: dict, overlay: dict) -> dict:
    result = base.copy()
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@lru_cache()
def get_settings() -> Settings:
    yaml_config = load_config_from_yaml()
    env_overrides = load_env_overrides()
    merged = _deep_merge(yaml_config, env_overrides)
    return Settings(**merged)


settings = get_settings()
