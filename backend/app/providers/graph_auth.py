import time

import msal

from app.core.config import Settings


class GraphTokenClient:
    """Acesso ao Microsoft Graph via OAuth2 On-Behalf-Of: o backend troca o
    token do usuário logado (audience = nossa própria API) por um token do
    Graph com escopos delegados, atuando em nome desse usuário — nunca com
    um token de aplicativo próprio. Cada instância é criada por requisição
    (veja app/api/v1/deps.py) e carrega o token do usuário daquela requisição.

    O cliente MSAL só é construído no primeiro uso — nunca no __init__ — para
    que instanciar um provider sem o Graph configurado não derrube a aplicação.
    """

    def __init__(self, settings: Settings, user_token: str | None):
        self._settings = settings
        self._user_token = user_token
        self._app: msal.ConfidentialClientApplication | None = None
        self._cache: dict[tuple[str, ...], tuple[str, float]] = {}

    def _obter_app(self) -> msal.ConfidentialClientApplication:
        if self._app is None:
            self._app = msal.ConfidentialClientApplication(
                client_id=self._settings.ms_graph_client_id,
                client_credential=self._settings.ms_graph_client_secret,
                authority=f"https://login.microsoftonline.com/{self._settings.ms_graph_tenant_id}",
            )
        return self._app

    async def obter_token(self, scopes: list[str]) -> str:
        # Checagens baratas (sem rede) antes de qualquer chamada que dependa
        # de credenciais reais — assim ficam com a mensagem certa mesmo
        # quando os valores configurados não são um tenant/app válido de verdade.
        if not self._settings.graph_configurado:
            raise RuntimeError(
                "Microsoft Graph não configurado (MS_GRAPH_TENANT_ID/CLIENT_ID/CLIENT_SECRET/GROUP_ID)"
            )
        if not self._user_token:
            raise RuntimeError("Sessão sem usuário autenticado — não é possível acessar o Microsoft Graph em nome dele")

        chave = tuple(sorted(scopes))
        em_cache = self._cache.get(chave)
        if em_cache and time.time() < em_cache[1] - 60:
            return em_cache[0]

        resultado = self._obter_app().acquire_token_on_behalf_of(user_assertion=self._user_token, scopes=scopes)
        if "access_token" not in resultado:
            detalhe = resultado.get("error_description", resultado)
            raise RuntimeError(f"Falha ao obter acesso ao Microsoft Graph em nome do usuário: {detalhe}")

        token = resultado["access_token"]
        self._cache[chave] = (token, time.time() + resultado.get("expires_in", 3600))
        return token

    async def headers(self, scopes: list[str]) -> dict[str, str]:
        token = await self.obter_token(scopes)
        return {"Authorization": f"Bearer {token}"}
