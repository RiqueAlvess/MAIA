import pytest

from app.core.config import Settings
from app.providers.email.graph_email import GraphEmailProvider
from app.providers.graph_auth import GraphTokenClient


def _settings_sem_graph(**overrides) -> Settings:
    valores = {
        "ms_graph_tenant_id": "",
        "ms_graph_client_id": "",
        "ms_graph_client_secret": "",
        "ms_graph_group_id": "",
    }
    valores.update(overrides)
    return Settings(**valores)


def _settings_configurado() -> Settings:
    return _settings_sem_graph(
        ms_graph_tenant_id="tenant-123",
        ms_graph_client_id="client-123",
        ms_graph_client_secret="segredo",
        ms_graph_group_id="grupo-123",
    )


def test_construir_provider_sem_graph_configurado_nao_levanta_excecao() -> None:
    token_client = GraphTokenClient(_settings_sem_graph(), user_token="token-do-usuario")
    GraphEmailProvider(token_client)


async def test_enviar_sem_graph_configurado_levanta_erro_claro() -> None:
    token_client = GraphTokenClient(_settings_sem_graph(), user_token="token-do-usuario")
    provider = GraphEmailProvider(token_client)

    with pytest.raises(RuntimeError, match="Microsoft Graph não configurado"):
        await provider.enviar(["destino@example.com"], "Assunto", "<p>corpo</p>")


async def test_enviar_com_graph_configurado_mas_sem_usuario_logado_levanta_erro_claro() -> None:
    # Graph configurado (credenciais de app válidas), mas sem um usuário
    # logado não há a quem representar no fluxo On-Behalf-Of.
    token_client = GraphTokenClient(_settings_configurado(), user_token=None)
    provider = GraphEmailProvider(token_client)

    with pytest.raises(RuntimeError, match="sem usuário autenticado"):
        await provider.enviar(["destino@example.com"], "Assunto", "<p>corpo</p>")


async def test_enviar_sem_destinatarios_levanta_value_error() -> None:
    token_client = GraphTokenClient(_settings_configurado(), user_token="token-do-usuario")
    provider = GraphEmailProvider(token_client)

    with pytest.raises(ValueError, match="destinatário"):
        await provider.enviar([], "Assunto", "<p>corpo</p>")
