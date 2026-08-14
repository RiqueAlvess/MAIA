import pytest

from app.core.config import Settings
from app.providers.graph_auth import GraphTokenClient
from app.providers.storage.graph_storage import GraphStorageProvider


def _settings_sem_graph(**overrides) -> Settings:
    valores = {
        "ms_graph_tenant_id": "",
        "ms_graph_client_id": "",
        "ms_graph_client_secret": "",
        "ms_graph_group_id": "",
    }
    valores.update(overrides)
    return Settings(**valores)


def test_construir_provider_sem_graph_configurado_nao_levanta_excecao() -> None:
    # O cliente MSAL só é construído no primeiro uso — nunca no __init__ —
    # para que instanciar o provider via Depends() nunca derrube a aplicação
    # antes de qualquer chamada de rede realmente acontecer.
    token_client = GraphTokenClient(_settings_sem_graph(), user_token="token-do-usuario")
    GraphStorageProvider(group_id="", token_client=token_client)


async def test_usar_provider_sem_graph_configurado_levanta_erro_claro() -> None:
    token_client = GraphTokenClient(_settings_sem_graph(), user_token="token-do-usuario")
    provider = GraphStorageProvider(group_id="", token_client=token_client)

    with pytest.raises(RuntimeError, match="Microsoft Graph não configurado"):
        await provider.listar_documentos("pasta-1")


async def test_usar_provider_com_graph_configurado_mas_sem_usuario_logado_levanta_erro_claro() -> None:
    settings = _settings_sem_graph(
        ms_graph_tenant_id="tenant-123",
        ms_graph_client_id="client-123",
        ms_graph_client_secret="segredo",
        ms_graph_group_id="grupo-123",
    )
    token_client = GraphTokenClient(settings, user_token=None)
    provider = GraphStorageProvider(group_id=settings.ms_graph_group_id, token_client=token_client)

    with pytest.raises(RuntimeError, match="sem usuário autenticado"):
        await provider.listar_documentos("pasta-1")
