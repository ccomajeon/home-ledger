from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "dev"
    backend_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:8000"
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
    session_cookie_name: str = "home_ledger_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 7
    local_admin_enabled: bool = False
    local_admin_username: str = "SYSTEM"
    local_admin_password_hash: str = ""
    local_admin_identity: str = "system@local"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "prod"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]

    @property
    def allowed_domains(self) -> set[str]:
        return {
            domain.strip().lower().removeprefix("@")
            for domain in self.allowed_email_domains.split(",")
            if domain.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
