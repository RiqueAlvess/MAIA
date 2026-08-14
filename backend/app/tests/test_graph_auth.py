import pytest

from app.core.config import Settings
from app.providers.graph_auth import GraphTokenClient


def _settings_configurado() -> Settings:
    return Settings(
        ms_graph_tenant_id="tenant-123",
        ms_graph_client_id="client-123",
        ms_graph_client_secret="segredo",
        ms_graph_group_id="grupo-123",
    )


def test_construir_cliente_sem_graph_configurado_nao_levanta_excecao() -> None:
    GraphTokenClient(Settings(ms_graph_tenant_id="", ms_graph_client_id="", ms_graph_client_secret=""), "token")


async def test_obter_token_sem_graph_configurado_levanta_erro_claro() -> None:
    cliente = GraphTokenClient(
        Settings(ms_graph_tenant_id="", ms_graph_client_id="", ms_graph_client_secret=""), "token"
    )

    with pytest.raises(RuntimeError, match="Microsoft Graph não configurado"):
        await cliente.obter_token(["Files.ReadWrite.All"])


async def test_obter_token_sem_usuario_autenticado_levanta_erro_claro() -> None:
    cliente = GraphTokenClient(_settings_configurado(), user_token=None)

    with pytest.raises(RuntimeError, match="sem usuário autenticado"):
        await cliente.obter_token(["Files.ReadWrite.All"])


async def test_obter_token_realiza_troca_on_behalf_of_e_usa_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas = []

    class AppFalso:
        def acquire_token_on_behalf_of(self, user_assertion, scopes):
            chamadas.append((user_assertion, tuple(scopes)))
            return {"access_token": "token-do-graph", "expires_in": 3600}

    cliente = GraphTokenClient(_settings_configurado(), user_token="token-do-usuario")
    cliente._obter_app = lambda: AppFalso()  # type: ignore[method-assign]

    token1 = await cliente.obter_token(["Files.ReadWrite.All"])
    token2 = await cliente.obter_token(["Files.ReadWrite.All"])

    assert token1 == "token-do-graph"
    assert token2 == "token-do-graph"
    assert len(chamadas) == 1  # segunda chamada veio do cache, não repetiu a troca OBO
    assert chamadas[0] == ("token-do-usuario", ("Files.ReadWrite.All",))


async def test_obter_token_repete_troca_para_escopos_diferentes(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas = []

    class AppFalso:
        def acquire_token_on_behalf_of(self, user_assertion, scopes):
            chamadas.append(tuple(scopes))
            return {"access_token": f"token-{'-'.join(scopes)}", "expires_in": 3600}

    cliente = GraphTokenClient(_settings_configurado(), user_token="token-do-usuario")
    cliente._obter_app = lambda: AppFalso()  # type: ignore[method-assign]

    await cliente.obter_token(["Files.ReadWrite.All"])
    await cliente.obter_token(["Mail.Send"])

    assert len(chamadas) == 2


async def test_obter_token_com_falha_na_troca_levanta_erro_com_detalhe(monkeypatch: pytest.MonkeyPatch) -> None:
    class AppFalso:
        def acquire_token_on_behalf_of(self, user_assertion, scopes):
            return {"error": "invalid_grant", "error_description": "token expirado"}

    cliente = GraphTokenClient(_settings_configurado(), user_token="token-do-usuario")
    cliente._obter_app = lambda: AppFalso()  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="token expirado"):
        await cliente.obter_token(["Files.ReadWrite.All"])
