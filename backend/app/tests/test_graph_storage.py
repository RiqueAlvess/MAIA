import pytest

from app.core.config import Settings
from app.providers.storage.graph_storage import GraphStorageProvider


def _settings_sem_graph() -> Settings:
    return Settings(ms_graph_tenant_id="", ms_graph_client_id="", ms_graph_client_secret="", ms_graph_site_id="")


def test_construir_provider_sem_graph_configurado_nao_levanta_excecao() -> None:
    # Antes da correção, o MSAL ConfidentialClientApplication era construído no
    # __init__, derrubando com ValueError qualquer request que dependesse deste
    # provider via Depends() — mesmo sem nenhuma chamada de rede ainda ter sido feita.
    GraphStorageProvider(_settings_sem_graph())


async def test_usar_provider_sem_graph_configurado_levanta_erro_claro() -> None:
    provider = GraphStorageProvider(_settings_sem_graph())

    with pytest.raises(RuntimeError, match="Microsoft Graph não configurado"):
        await provider.listar_documentos("pasta-1")
