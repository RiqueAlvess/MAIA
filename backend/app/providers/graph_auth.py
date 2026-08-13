import time

import msal

from app.core.config import Settings

GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]


class GraphTokenClient:
    """Autenticação app-only (client credentials) compartilhada por todos os
    providers que falam com o Microsoft Graph (storage, e-mail). O cliente MSAL
    só é construído no primeiro uso — nunca no __init__ — para que instanciar um
    provider sem o Graph configurado não derrube a aplicação."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._app: msal.ConfidentialClientApplication | None = None
        self._token: str | None = None
        self._token_expira_em: float = 0.0

    def _obter_app(self) -> msal.ConfidentialClientApplication:
        if not self._settings.graph_configurado:
            raise RuntimeError("Microsoft Graph não configurado (MS_GRAPH_TENANT_ID/CLIENT_ID/CLIENT_SECRET)")
        if self._app is None:
            self._app = msal.ConfidentialClientApplication(
                client_id=self._settings.ms_graph_client_id,
                client_credential=self._settings.ms_graph_client_secret,
                authority=f"https://login.microsoftonline.com/{self._settings.ms_graph_tenant_id}",
            )
        return self._app

    async def obter_token(self) -> str:
        if self._token and time.time() < self._token_expira_em - 60:
            return self._token
        resultado = self._obter_app().acquire_token_for_client(scopes=GRAPH_SCOPE)
        if "access_token" not in resultado:
            detalhe = resultado.get("error_description", resultado)
            raise RuntimeError(f"Falha ao autenticar no Microsoft Graph: {detalhe}")
        self._token = resultado["access_token"]
        self._token_expira_em = time.time() + resultado.get("expires_in", 3600)
        return self._token

    async def headers(self) -> dict[str, str]:
        token = await self.obter_token()
        return {"Authorization": f"Bearer {token}"}
