from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"

    database_url: str = "sqlite+aiosqlite:///./data/maia.db"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"
    anthropic_max_tokens: int = 4000

    ms_graph_tenant_id: str = ""
    ms_graph_client_id: str = ""
    ms_graph_client_secret: str = ""
    ms_graph_site_id: str = ""

    entra_tenant_id: str = ""
    entra_audience: str = ""

    cors_allowed_origins: str = "http://localhost:4200"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origem.strip() for origem in self.cors_allowed_origins.split(",") if origem.strip()]

    @property
    def ai_configurado(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def graph_configurado(self) -> bool:
        return bool(self.ms_graph_tenant_id and self.ms_graph_client_id and self.ms_graph_client_secret)

    @property
    def auth_configurado(self) -> bool:
        return bool(self.entra_tenant_id and self.entra_audience)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def garantir_diretorio_sqlite(database_url: str) -> None:
    """Cria o diretório do arquivo .db se a URL apontar para um banco SQLite local."""
    if not database_url.startswith("sqlite"):
        return
    caminho_arquivo = database_url.split("///", 1)[-1]
    if caminho_arquivo and caminho_arquivo != ":memory:":
        Path(caminho_arquivo).parent.mkdir(parents=True, exist_ok=True)
