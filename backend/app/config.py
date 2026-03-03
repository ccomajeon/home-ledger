from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "dev"
    backend_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:5173"
    session_secret: str = "change-me"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    owner_email: str = "owner@example.com"
    allowed_email_domains: str = ""
    cors_allow_origins: str = "http://localhost:5173"
    db_url: str = "sqlite:///./data/app.db"
    backup_dir: str = "./data/backups"
    dev_auth_bypass: bool = False

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "prod"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

