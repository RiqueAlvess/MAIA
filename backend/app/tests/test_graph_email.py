import pytest

from app.core.config import Settings
from app.providers.email.graph_email import GraphEmailProvider


def _settings_sem_email(**overrides) -> Settings:
    valores = {
        "ms_graph_tenant_id": "",
        "ms_graph_client_id": "",
        "ms_graph_client_secret": "",
        "ms_graph_sender_upn": "",
    }
    valores.update(overrides)
    return Settings(**valores)


def test_construir_provider_sem_email_configurado_nao_levanta_excecao() -> None:
    GraphEmailProvider(_settings_sem_email())


async def test_enviar_sem_graph_configurado_levanta_erro_claro() -> None:
    provider = GraphEmailProvider(_settings_sem_email())

    with pytest.raises(RuntimeError, match="Envio de e-mail não configurado"):
        await provider.enviar(["destino@example.com"], "Assunto", "<p>corpo</p>")


async def test_enviar_com_graph_configurado_mas_sem_remetente_levanta_erro_claro() -> None:
    # Graph configurado (storage funcionaria), mas sem MS_GRAPH_SENDER_UPN o
    # envio de e-mail continua indisponível — são capacidades independentes.
    provider = GraphEmailProvider(
        _settings_sem_email(
            ms_graph_tenant_id="tenant-123",
            ms_graph_client_id="client-123",
            ms_graph_client_secret="segredo",
        )
    )

    with pytest.raises(RuntimeError, match="Envio de e-mail não configurado"):
        await provider.enviar(["destino@example.com"], "Assunto", "<p>corpo</p>")


async def test_enviar_sem_destinatarios_levanta_value_error() -> None:
    provider = GraphEmailProvider(
        _settings_sem_email(
            ms_graph_tenant_id="tenant-123",
            ms_graph_client_id="client-123",
            ms_graph_client_secret="segredo",
            ms_graph_sender_upn="maia@lgconsult.com.br",
        )
    )

    with pytest.raises(ValueError, match="destinatário"):
        await provider.enviar([], "Assunto", "<p>corpo</p>")
